"""Base validator interface for commit message validation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]

    @classmethod
    def ok(cls) -> "ValidationResult":
        return cls(valid=True, errors=[], warnings=[])

    @classmethod
    def fail(cls, errors: list[str]) -> "ValidationResult":
        return cls(valid=False, errors=errors, warnings=[])

    def error_summary(self) -> str:
        return "\n".join(self.errors)


class ValidatorBase(ABC):
    @abstractmethod
    def validate(self, message: str) -> ValidationResult:
        """Validate a commit message. Returns ValidationResult."""
        ...

    @abstractmethod
    def get_rules_prompt(self) -> str:
        """Return a prompt fragment describing the validation rules."""
        ...
