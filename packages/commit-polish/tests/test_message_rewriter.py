"""Tests for the message rewriter orchestration."""

import pytest
from unittest.mock import AsyncMock, patch

from commit_polish.config import Config
from commit_polish.message_rewriter import rewrite_message
from commit_polish.validators.base import ValidatorBase, ValidationResult


class PassValidator(ValidatorBase):
    def validate(self, message: str) -> ValidationResult:
        return ValidationResult.ok()

    def get_rules_prompt(self) -> str:
        return "Always pass."


class FailThenPassValidator(ValidatorBase):
    def __init__(self) -> None:
        self.calls = 0

    def validate(self, message: str) -> ValidationResult:
        self.calls += 1
        if self.calls == 1:
            return ValidationResult.fail(["Missing type prefix"])
        return ValidationResult.ok()

    def get_rules_prompt(self) -> str:
        return "Must have type prefix."


class AlwaysFailValidator(ValidatorBase):
    def validate(self, message: str) -> ValidationResult:
        return ValidationResult.fail(["Always fails"])

    def get_rules_prompt(self) -> str:
        return "Impossible to satisfy."


@pytest.fixture
def config() -> Config:
    return Config()


@pytest.mark.asyncio
async def test_successful_rewrite_no_validators(config: Config) -> None:
    with patch(
        "commit_polish.message_rewriter.generate_commit_message",
        new_callable=AsyncMock,
        return_value="feat: add login button",
    ):
        result = await rewrite_message(
            diff="+ button component",
            original_message="add button",
            config=config,
            validators=[],
        )
    assert result.message == "feat: add login button"
    assert result.attempts == 1
    assert result.validation_errors == []


@pytest.mark.asyncio
async def test_passes_validator_on_first_try(config: Config) -> None:
    with patch(
        "commit_polish.message_rewriter.generate_commit_message",
        new_callable=AsyncMock,
        return_value="fix: resolve null pointer",
    ):
        result = await rewrite_message(
            diff="- nullable field",
            original_message="fix null",
            config=config,
            validators=[PassValidator()],
        )
    assert result.message == "fix: resolve null pointer"
    assert result.attempts == 1


@pytest.mark.asyncio
async def test_retries_on_validation_failure(config: Config) -> None:
    validator = FailThenPassValidator()
    call_count = 0

    async def mock_generate(*args: object, **kwargs: object) -> str:
        nonlocal call_count
        call_count += 1
        return "feat: add feature" if call_count > 1 else "add feature"

    with patch(
        "commit_polish.message_rewriter.generate_commit_message",
        side_effect=mock_generate,
    ):
        result = await rewrite_message(
            diff="",
            original_message="add feature",
            config=config,
            validators=[validator],
        )

    assert result.attempts == 2
    assert validator.calls == 2


@pytest.mark.asyncio
async def test_max_retries_exhausted_returns_last_message(config: Config) -> None:
    config.validation.max_retries = 2
    with patch(
        "commit_polish.message_rewriter.generate_commit_message",
        new_callable=AsyncMock,
        return_value="bad message",
    ):
        result = await rewrite_message(
            diff="",
            original_message="bad",
            config=config,
            validators=[AlwaysFailValidator()],
        )
    assert result.message == "bad message"
    assert result.attempts == 2
    assert "Always fails" in result.validation_errors


@pytest.mark.asyncio
async def test_on_attempt_callback_called(config: Config) -> None:
    attempts_seen: list[tuple[int, str]] = []

    def callback(attempt: int, msg: str) -> None:
        attempts_seen.append((attempt, msg))

    with patch(
        "commit_polish.message_rewriter.generate_commit_message",
        new_callable=AsyncMock,
        return_value="chore: update deps",
    ):
        await rewrite_message(
            diff="",
            original_message="update",
            config=config,
            validators=[],
            on_attempt=callback,
        )

    assert attempts_seen == [(1, "chore: update deps")]
