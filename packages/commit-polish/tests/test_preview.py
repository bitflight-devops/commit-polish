"""Tests for the preview CLI command."""

import pytest
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from commit_polish.cli import app
from commit_polish.message_rewriter import RewriteResult
from commit_polish.ai_service import AIServiceError


runner = CliRunner()


def _mock_rewrite(message: str = "feat: add feature") -> MagicMock:
    result = RewriteResult(message=message, attempts=1, validation_errors=[])
    mock = MagicMock(return_value=result)
    return mock


def test_preview_no_staged_changes_no_message() -> None:
    with patch("commit_polish.cli.get_staged_diff", return_value=""):
        result = runner.invoke(app, ["preview"])
    assert result.exit_code == 0
    assert "No staged changes" in result.output


def test_preview_with_message_only() -> None:
    mock_rewrite = _mock_rewrite("fix: correct typo in README")
    with (
        patch("commit_polish.cli.get_staged_diff", return_value=""),
        patch("commit_polish.cli.rewrite_message_sync", mock_rewrite),
    ):
        result = runner.invoke(app, ["preview", "--message", "fix typo"])
    assert result.exit_code == 0
    assert "fix: correct typo in README" in result.output


def test_preview_with_diff_file(tmp_path: Path) -> None:
    diff_file = tmp_path / "changes.patch"
    diff_file.write_text("+ new feature code\n- old code\n")
    mock_rewrite = _mock_rewrite("feat: implement new feature")
    with patch("commit_polish.cli.rewrite_message_sync", mock_rewrite):
        result = runner.invoke(app, ["preview", "--diff", str(diff_file)])
    assert result.exit_code == 0
    assert "feat: implement new feature" in result.output


def test_preview_diff_file_not_found(tmp_path: Path) -> None:
    result = runner.invoke(app, ["preview", "--diff", str(tmp_path / "missing.patch")])
    assert result.exit_code == 1
    assert "not found" in result.output


def test_preview_llm_unavailable_shows_error() -> None:
    with (
        patch("commit_polish.cli.get_staged_diff", return_value="some diff"),
        patch(
            "commit_polish.cli.rewrite_message_sync",
            side_effect=AIServiceError("Connection refused"),
        ),
    ):
        result = runner.invoke(app, ["preview"])
    assert result.exit_code == 1
    assert "Connection refused" in result.output


def test_preview_shows_validation_warnings() -> None:
    result_with_warnings = RewriteResult(
        message="feat: add thing",
        attempts=3,
        validation_errors=["subject-case: must be lower-case"],
    )
    with (
        patch("commit_polish.cli.get_staged_diff", return_value="+ code"),
        patch("commit_polish.cli.rewrite_message_sync", return_value=result_with_warnings),
    ):
        result = runner.invoke(app, ["preview"])
    assert "subject-case" in result.output


def test_preview_shows_attempt_count_when_retried() -> None:
    multi_attempt = RewriteResult(message="fix: corrected", attempts=3, validation_errors=[])
    with (
        patch("commit_polish.cli.get_staged_diff", return_value="+ fix"),
        patch("commit_polish.cli.rewrite_message_sync", return_value=multi_attempt),
    ):
        result = runner.invoke(app, ["preview"])
    assert "3 attempt" in result.output


def test_config_init_creates_file(tmp_path: Path) -> None:
    target = tmp_path / "config.toml"
    result = runner.invoke(app, ["config", "init", "--path", str(target)])
    assert result.exit_code == 0
    assert target.exists()
    assert "written" in result.output.lower()


def test_config_init_warns_if_exists(tmp_path: Path) -> None:
    target = tmp_path / "config.toml"
    target.write_text("[ai]\nmodel = 'x'")
    result = runner.invoke(app, ["config", "init", "--path", str(target)])
    assert result.exit_code == 0
    assert "already exists" in result.output


def test_config_show_missing(tmp_path: Path) -> None:
    result = runner.invoke(app, ["config", "show", "--path", str(tmp_path / "x.toml")])
    assert "No config found" in result.output


def test_config_show_existing(tmp_path: Path) -> None:
    target = tmp_path / "config.toml"
    target.write_text("[ai]\nmodel = 'llamafile/test'\ntemperature = 0.5\nmax_tokens = 100\n")
    result = runner.invoke(app, ["config", "show", "--path", str(target)])
    assert "llamafile/test" in result.output
