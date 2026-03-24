"""Tests for the config module."""

import pytest
from pathlib import Path
import tomlkit

from commit_polish.config import (
    load_config,
    write_default_config,
    Config,
    DEFAULT_SYSTEM_PROMPT,
)


def test_load_defaults_when_no_file(tmp_path: Path) -> None:
    config = load_config(tmp_path / "nonexistent.toml")
    assert config.ai.model == "llamafile/gemma-3-3b"
    assert config.ai.temperature == 0.3
    assert config.ai.max_tokens == 200
    assert config.validation.max_retries == 3
    assert config.validation.auto_detect is True


def test_load_from_file(tmp_path: Path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        """
[ai]
model = "llamafile/llama-3.2-3b"
temperature = 0.1
max_tokens = 150

[validation]
max_retries = 5
auto_detect = false
"""
    )
    config = load_config(config_file)
    assert config.ai.model == "llamafile/llama-3.2-3b"
    assert config.ai.temperature == 0.1
    assert config.ai.max_tokens == 150
    assert config.validation.max_retries == 5
    assert config.validation.auto_detect is False


def test_system_prompt_uses_default_when_empty(tmp_path: Path) -> None:
    config = load_config(tmp_path / "missing.toml")
    assert config.system_prompt() == DEFAULT_SYSTEM_PROMPT


def test_system_prompt_uses_custom(tmp_path: Path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text('[validation]\nsystem_prompt = "Custom prompt"')
    config = load_config(config_file)
    assert config.system_prompt() == "Custom prompt"


def test_write_default_config(tmp_path: Path) -> None:
    path = tmp_path / "sub" / "config.toml"
    written = write_default_config(path)
    assert written == path
    assert path.exists()
    doc = tomlkit.loads(path.read_text())
    assert doc["ai"]["model"] == "llamafile/gemma-3-3b"
    assert doc["validation"]["auto_detect"] is True


def test_write_default_config_creates_parents(tmp_path: Path) -> None:
    deep = tmp_path / "a" / "b" / "c" / "config.toml"
    write_default_config(deep)
    assert deep.exists()
