"""Orchestrates LLM generation with optional validation feedback loop."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from commit_polish.ai_service import generate_commit_message, AIServiceError
from commit_polish.config import Config
from commit_polish.validators.base import ValidatorBase


@dataclass
class RewriteResult:
    message: str
    attempts: int
    validation_errors: list[str]
    skipped: bool = False  # True if LLM was unavailable and original was kept


async def rewrite_message(
    diff: str,
    original_message: str,
    config: Config,
    validators: list[ValidatorBase],
    on_attempt: object = None,  # Optional callback(attempt_num, message) for progress
) -> RewriteResult:
    """Rewrite a commit message using the LLM, with validation retry loop.

    Args:
        diff: Staged git diff.
        original_message: The commit message to polish.
        config: Loaded config.
        validators: List of validators to run after generation.
        on_attempt: Optional callback called with (attempt: int, message: str).

    Returns:
        RewriteResult with the final message.
    """
    system_prompt = config.system_prompt()

    # Append validator rule hints to the system prompt
    if validators:
        rules = "\n".join(v.get_rules_prompt() for v in validators)
        system_prompt = f"{system_prompt}\n\nValidation rules:\n{rules}"

    extra_context = ""
    last_errors: list[str] = []
    last_message = original_message

    for attempt in range(1, config.validation.max_retries + 1):
        try:
            message = await generate_commit_message(
                diff=diff,
                original_message=original_message,
                system_prompt=system_prompt,
                config=config,
                extra_context=extra_context,
            )
        except AIServiceError:
            raise

        if callable(on_attempt):
            on_attempt(attempt, message)

        last_message = message

        # Run validators
        all_errors: list[str] = []
        for validator in validators:
            result = validator.validate(message)
            if not result.valid:
                all_errors.extend(result.errors)

        if not all_errors:
            return RewriteResult(
                message=message,
                attempts=attempt,
                validation_errors=[],
            )

        last_errors = all_errors
        error_text = "\n".join(all_errors)
        extra_context = (
            f"The previous attempt failed validation with these errors:\n{error_text}\n"
            "Please fix these issues in your next commit message."
        )

    # Max retries exhausted — return last generated message with errors noted
    return RewriteResult(
        message=last_message,
        attempts=config.validation.max_retries,
        validation_errors=last_errors,
    )


def rewrite_message_sync(
    diff: str,
    original_message: str,
    config: Config,
    validators: list[ValidatorBase],
    on_attempt: object = None,
) -> RewriteResult:
    """Synchronous wrapper around rewrite_message."""
    return asyncio.run(
        rewrite_message(
            diff=diff,
            original_message=original_message,
            config=config,
            validators=validators,
            on_attempt=on_attempt,
        )
    )
