"""Auto-detect validator configurations in the current project."""

from __future__ import annotations

import subprocess
from pathlib import Path

from commit_polish.validators.base import ValidatorBase, ValidationResult


COMMITLINT_CONFIG_FILES = [
    "commitlint.config.js",
    "commitlint.config.cjs",
    "commitlint.config.mjs",
    ".commitlintrc",
    ".commitlintrc.json",
    ".commitlintrc.yaml",
    ".commitlintrc.yml",
    ".commitlintrc.js",
]

SEMANTIC_RELEASE_FILES = [
    "release.config.js",
    "release.config.cjs",
    ".releaserc",
    ".releaserc.json",
    ".releaserc.yaml",
    ".releaserc.yml",
]

COMMITIZEN_FILES = [
    ".cz.json",
    ".cz.toml",
    ".cz.yaml",
    ".cz.yml",
    "cz.json",
]


def _find_config(filenames: list[str], root: Path) -> Path | None:
    for name in filenames:
        p = root / name
        if p.exists():
            return p
    return None


class CommitlintValidator(ValidatorBase):
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path

    def validate(self, message: str) -> ValidationResult:
        try:
            result = subprocess.run(
                ["npx", "commitlint", "--edit", "-"],
                input=message,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return ValidationResult.ok()
            errors = [
                line for line in result.stdout.splitlines() if line.strip()
            ]
            return ValidationResult.fail(errors or ["commitlint validation failed"])
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return ValidationResult.ok()  # Validator unavailable — skip

    def get_rules_prompt(self) -> str:
        return (
            f"Follow the commitlint rules defined in {self.config_path.name}. "
            "Use Conventional Commits format strictly."
        )


class CommandValidator(ValidatorBase):
    """Runs an arbitrary shell command to validate the commit message."""

    def __init__(self, command: str) -> None:
        self.command = command

    def validate(self, message: str) -> ValidationResult:
        try:
            result = subprocess.run(
                self.command,
                shell=True,
                input=message,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return ValidationResult.ok()
            errors = [
                line for line in (result.stdout + result.stderr).splitlines()
                if line.strip()
            ]
            return ValidationResult.fail(errors or ["Validation command failed"])
        except subprocess.TimeoutExpired:
            return ValidationResult.ok()

    def get_rules_prompt(self) -> str:
        return f"The commit message will be validated by: {self.command}"


def detect_validators(
    root: Path | None = None,
    validator_command: str = "",
    auto_detect: bool = True,
) -> list[ValidatorBase]:
    """Detect available validators in the project root."""
    validators: list[ValidatorBase] = []

    if validator_command:
        validators.append(CommandValidator(validator_command))
        return validators

    if not auto_detect:
        return validators

    project_root = root or Path.cwd()

    commitlint_cfg = _find_config(COMMITLINT_CONFIG_FILES, project_root)
    if commitlint_cfg:
        validators.append(CommitlintValidator(commitlint_cfg))

    return validators
