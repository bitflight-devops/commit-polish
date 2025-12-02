# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**commit-polish** is a two-package pre-commit hook system that automatically rewrites git commit messages to specified formats (conventional commits, JIRA style, etc.) using local LLMs via LiteLLM.

### Key Architecture Principles

1. **Separation of Concerns**: The hook runtime (`commit-polish`) is separate from the setup tool (`commit-polish-installer`)
2. **LiteLLM Routing**: All LLM calls use LiteLLM's routing system with native llamafile support
3. **XDG Compliance**: Configuration follows XDG Base Directory specifications

## Development Commands

### Package Structure Setup
```bash
# Create the monorepo structure for two packages
mkdir -p packages/commit-polish/src/commit_polish
mkdir -p packages/commit-polish-installer/src/commit_polish_installer

# Initialize packages with uv
cd packages/commit-polish && uv init
cd packages/commit-polish-installer && uv init
```

### Testing Commands
```bash
# Run tests for commit-polish package
cd packages/commit-polish
uv run pytest tests/

# Run tests for installer package
cd packages/commit-polish-installer
uv run pytest tests/

# Test hook manually without committing
uv run commit-polish test --message "test message" --diff path/to/diff
```

### Linting and Type Checking
```bash
# Run ruff linter
uv run ruff check src/ tests/

# Run mypy type checker
uv run mypy src/

# Format with ruff
uv run ruff format src/ tests/
```

### Installation Testing
```bash
# Test installer locally
cd packages/commit-polish-installer
uv run commit-polish-install --dry-run

# Test hook activation
pre-commit install --hook-type prepare-commit-msg
pre-commit run --hook-stage prepare-commit-msg
```

## High-Level Architecture

### Package 1: commit-polish (The Hook)

**Purpose**: Lightweight runtime hook that reads config and rewrites commit messages.

**Key Components**:
- `hook.py`: Entry point for prepare-commit-msg hook (receives message file path in sys.argv[1])
- `ai_service.py`: LiteLLM wrapper with llamafile routing (uses `llamafile/` prefix)
- `config.py`: TOML config loader using `tomlkit` (preserves formatting and comments)
- `validators/`: Integration with external validators (commitlint, custom scripts)
- `message_rewriter.py`: Orchestrates LLM generation with validation feedback loop

**Critical Details**:
- Hook stage MUST be `prepare-commit-msg` (not `commit-msg`) for message rewriting
- LiteLLM llamafile models use prefix `llamafile/` for automatic routing
- Default API base for llamafile is `http://127.0.0.1:8080/v1` (port 8080, not 8000)
- No installation logic - assumes config exists at `~/.config/commit-polish/config.toml`

### Package 2: commit-polish-installer (The Setup Tool)

**Purpose**: User-facing tool that downloads llamafile, creates config, and sets up pre-commit.

**Key Components**:
- `llamafile_installer.py`: Downloads Mozilla llamafile v0.9.3 from GitHub releases
- `config_generator.py`: Creates TOML config using `tomlkit` (preserves formatting and comments)
- `hook_installer.py`: Runs `pre-commit install --hook-type prepare-commit-msg`
- `paths.py`: XDG Base Directory paths management

**Critical URLs and Versions**:
- Llamafile version: 0.9.3
- Download URL: `https://github.com/mozilla-ai/llamafile/releases/download/0.9.3/llamafile-0.9.3`
- Llamafile command: `./llamafile --server -m model.gguf --nobrowser --port 8080 --host 127.0.0.1`

## Technical Specifications

### Pre-commit Hook Configuration
The `.pre-commit-hooks.yaml` MUST use:
- `stages: [prepare-commit-msg]` - for message rewriting capability
- `pass_filenames: false` - hook doesn't process files
- `always_run: true` - run even without file changes

### LiteLLM Integration
- Models with `llamafile/` prefix route to llamafile server
- Exception handling: `litellm.APIConnectionError` (not `.exceptions.APIConnectionError`)
- Async API: `litellm.acompletion()` for async calls
- No API key required for llamafile models

### Configuration File
Location: `~/.config/commit-polish/config.toml`

Required structure:
```toml
[ai]
model = "llamafile/gemma-3-3b"  # Must use llamafile/ prefix
temperature = 0.3
max_tokens = 200

[llamafile]
path = "/path/to/llamafile"
model_path = "/path/to/model.gguf"

[validation]
# Auto-detect validators: commitlint, semantic-release, commitizen configs
auto_detect = true

# Optional: Custom validator command
# validator_command = "npx commitlint --from HEAD~1"

# Optional: Custom system prompt (overrides default)
# system_prompt = "Your custom instructions here"

# Retry logic
max_retries = 3
```

**Default System Prompt** (used when no validator config found):
```
Write a commit message in the Conventional Commits format. Use the structure:
    <type>(<optional scope>): <short description>

    <optional body>

    <optional footer>

Example types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
Optionally, include a body for more details in bullet points.
Optionally, in the footer, use BREAKING CHANGE: followed by a detailed explanation of the breaking change.

Just return the commit message, do not include any other text.
```

**Validator Integration**:
- If `commitlint.config.js`, `.commitlintrc`, or similar configs are found, their rules are passed to the LLM as context
- The LLM generates a message, then the validator checks it
- If validation fails, errors are fed back to the LLM for self-correction (max 3 retries)
- If `release.config.js` (semantic-release) or `.cz.json` (commitizen) exist, approved commit types are extracted and included in the prompt

## Development Workflow

1. **Phase 1**: Implement `commit-polish` hook package
   - Core modules: config, ai_service, hook, validators, message_rewriter
   - Validator detection: auto-find commitlint, semantic-release, commitizen configs
   - Validation loop: LLM generates → validator checks → retry with errors if needed
   - Verify hook receives correct arguments from pre-commit
   - Test with mock LLM responses and real validators

2. **Phase 2**: Implement `commit-polish-installer` package
   - Download llamafile binary and make executable (chmod 755)
   - Generate config with correct model prefix
   - Run pre-commit installation

3. **Phase 3**: Integration testing
   - Test full flow: install → commit → rewrite
   - Verify llamafile server starts on port 8080
   - Test with real Gemma 3B model

## Important Implementation Notes

- Python 3.11+ required (uses `tomlkit` for TOML parsing with format preservation)
- Hook should NEVER start llamafile server (installer's responsibility)
- Use `uv` for package management and `uvx` for installation
- Default model: Gemma 3 3B (~2GB download) for balance of speed and quality
- Config uses TOML format (not YAML or JSON) for human readability

## Common Pitfalls to Avoid

1. Don't use `commit-msg` hook stage - use `prepare-commit-msg` for rewriting
2. Don't forget the `llamafile/` prefix for LiteLLM routing
3. Don't use port 8000 - llamafile defaults to port 8080
4. Don't try to import `litellm.exceptions` - use `litellm.APIConnectionError` directly
5. Don't have the hook start servers - that's the installer's job