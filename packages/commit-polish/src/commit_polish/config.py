"""Configuration loader for commit-polish.

Reads from ~/.config/commit-polish/config.toml (XDG compliant).
Uses tomlkit to preserve formatting and comments on write.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import tomlkit

DEFAULT_SYSTEM_PROMPT = """\
Write a commit message in the Conventional Commits format. Use the structure:
    <type>(<optional scope>): <short description>

    <optional body>

    <optional footer>

Example types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
Optionally, include a body for more details in bullet points.
Optionally, in the footer, use BREAKING CHANGE: followed by a detailed explanation.

Just return the commit message, do not include any other text.\
"""

DEFAULT_CONFIG_PATH = (
    Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    / "commit-polish"
    / "config.toml"
)


@dataclass
class AIConfig:
    model: str = "llamafile/gemma-3-3b"
    temperature: float = 0.3
    max_tokens: int = 200
    api_base: str = "http://127.0.0.1:8080/v1"


@dataclass
class LlamafileConfig:
    path: str = ""
    model_path: str = ""


@dataclass
class ValidationConfig:
    auto_detect: bool = True
    validator_command: str = ""
    system_prompt: str = ""
    max_retries: int = 3


@dataclass
class Config:
    ai: AIConfig = field(default_factory=AIConfig)
    llamafile: LlamafileConfig = field(default_factory=LlamafileConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    config_path: Path = field(default_factory=lambda: DEFAULT_CONFIG_PATH)

    def system_prompt(self) -> str:
        return self.validation.system_prompt or DEFAULT_SYSTEM_PROMPT


def load_config(path: Path | None = None) -> Config:
    """Load config from TOML file. Falls back to defaults if file missing."""
    config_path = path or DEFAULT_CONFIG_PATH

    if not config_path.exists():
        return Config(config_path=config_path)

    raw = tomlkit.loads(config_path.read_text())

    ai_section = raw.get("ai", {})
    llamafile_section = raw.get("llamafile", {})
    validation_section = raw.get("validation", {})

    return Config(
        ai=AIConfig(
            model=str(ai_section.get("model", "llamafile/gemma-3-3b")),
            temperature=float(ai_section.get("temperature", 0.3)),
            max_tokens=int(ai_section.get("max_tokens", 200)),
            api_base=str(ai_section.get("api_base", "http://127.0.0.1:8080/v1")),
        ),
        llamafile=LlamafileConfig(
            path=str(llamafile_section.get("path", "")),
            model_path=str(llamafile_section.get("model_path", "")),
        ),
        validation=ValidationConfig(
            auto_detect=bool(validation_section.get("auto_detect", True)),
            validator_command=str(validation_section.get("validator_command", "")),
            system_prompt=str(validation_section.get("system_prompt", "")),
            max_retries=int(validation_section.get("max_retries", 3)),
        ),
        config_path=config_path,
    )


def write_default_config(path: Path | None = None) -> Path:
    """Write a default config file, creating parent directories as needed."""
    config_path = path or DEFAULT_CONFIG_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)

    doc = tomlkit.document()
    doc.add(tomlkit.comment("commit-polish configuration"))
    doc.add(tomlkit.nl())

    ai = tomlkit.table()
    ai.add(tomlkit.comment("Model to use for commit message generation"))
    ai.add(tomlkit.comment("Use 'llamafile/<model-name>' for local llamafile models"))
    ai.add("model", "llamafile/gemma-3-3b")
    ai.add("temperature", 0.3)
    ai.add("max_tokens", 200)
    doc.add("ai", ai)

    llamafile = tomlkit.table()
    llamafile.add("path", "")
    llamafile.add("model_path", "")
    doc.add("llamafile", llamafile)

    validation = tomlkit.table()
    validation.add(
        tomlkit.comment("Auto-detect commitlint, semantic-release, commitizen configs")
    )
    validation.add("auto_detect", True)
    validation.add("max_retries", 3)
    doc.add("validation", validation)

    config_path.write_text(tomlkit.dumps(doc))
    return config_path
