# uv Reference Documentation

## Overview

uv is an extremely fast Python package and project manager written in Rust by Astral. It replaces pip, pip-tools, pipx, poetry, pyenv, and virtualenv with a single tool.

**Key Feature for commit-polish**: uv manages the monorepo structure with two packages (commit-polish and commit-polish-installer).

## Official Documentation

- [uv Documentation](https://docs.astral.sh/uv/) - Primary reference
- [GitHub Repository](https://github.com/astral-sh/uv)
- [Workspaces Guide](https://docs.astral.sh/uv/concepts/projects/workspaces/)
- [Dependencies Reference](https://docs.astral.sh/uv/concepts/dependencies/)
- [CLI Reference](https://docs.astral.sh/uv/reference/cli/)
- [Projects Guide](https://docs.astral.sh/uv/guides/projects/)
- [PyPI Package](https://pypi.org/project/uv/)

## Installation

```bash
# Using curl (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Using pip
pip install uv

# Using Homebrew (macOS)
brew install uv

# Using pipx
pipx install uv

# Windows PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Project Initialization

### Create New Project

```bash
# Initialize in new directory
uv init my-project

# Initialize in current directory
uv init

# Initialize as application (default)
uv init --app my-app

# Initialize as library (includes build-system)
uv init --lib my-lib

# Initialize with package structure (distributable application)
uv init --package my-pkg

# Bare init (minimal pyproject.toml only)
uv init --bare

# Specify build backend
uv init --build-backend uv    # Uses uv_build (default for --lib/--package)
uv init --build-backend hatch # Uses hatchling
uv init --build-backend flit  # Uses flit-core

# Initialize as PEP 723 script
uv init --script example.py
```

### Generated pyproject.toml (Application - Default)

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.11"
dependencies = []
```

### Generated pyproject.toml (Library with --lib)

```toml
[project]
name = "example-lib"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.11"
dependencies = []

[build-system]
requires = ["uv_build>=0.9.2,<0.10.0"]
build-backend = "uv_build"
```

### Generated pyproject.toml (Packaged Application with --package)

```toml
[project]
name = "my-pkg"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.11"
dependencies = []

[project.scripts]
my-pkg = "my_pkg:main"

[build-system]
requires = ["uv_build>=0.9.2,<0.10.0"]
build-backend = "uv_build"
```

## Workspace Configuration

Workspaces organize large codebases by splitting them into multiple packages with common dependencies. All workspace members share a single lockfile (`uv.lock`).

### Root pyproject.toml (Workspace Configuration)

```toml
[project]
name = "commit-polish-workspace"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[tool.uv.workspace]
members = ["packages/*"]
exclude = ["packages/experimental"]

[tool.uv.sources]
commit-polish = { workspace = true }
commit-polish-installer = { workspace = true }

[build-system]
requires = ["uv_build>=0.9.2,<0.10.0"]
build-backend = "uv_build"
```

### Workspace Member Configuration

```toml
# packages/commit-polish/pyproject.toml
[project]
name = "commit-polish"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "litellm>=1.0.0",
]

[project.scripts]
commit-polish = "commit_polish.hook:main"

[build-system]
requires = ["uv_build>=0.9.2,<0.10.0"]
build-backend = "uv_build"
```

### Workspace Directory Structure

```
commit-polish/
├── pyproject.toml              # Root workspace config
├── uv.lock                     # Shared lockfile for all members
├── packages/
│   ├── commit-polish/
│   │   ├── pyproject.toml      # Hook package config
│   │   └── src/
│   │       └── commit_polish/
│   │           ├── __init__.py
│   │           ├── hook.py
│   │           ├── ai_service.py
│   │           └── config.py
│   └── commit-polish-installer/
│       ├── pyproject.toml      # Installer package config
│       └── src/
│           └── commit_polish_installer/
│               ├── __init__.py
│               ├── llamafile_installer.py
│               └── config_generator.py
└── README.md
```

### Path Dependencies (Alternative to Workspaces)

For cases requiring separate virtual environments per package:

```toml
[project]
name = "albatross"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["bird-feeder"]

[tool.uv.sources]
bird-feeder = { path = "packages/bird-feeder" }

[build-system]
requires = ["uv_build>=0.9.2,<0.10.0"]
build-backend = "uv_build"
```

## Dependency Management

### Adding Dependencies

```bash
# Add to project dependencies
uv add requests

# Add with version constraint
uv add "requests>=2.28,<3"
uv add "requests==2.31.0"

# Add development dependency (uses dependency-groups.dev)
uv add --dev pytest

# Add to specific dependency group
uv add --group lint ruff
uv add --group test pytest-cov

# Add optional dependency
uv add --optional network httpx

# Add from git
uv add git+https://github.com/encode/httpx
uv add git+https://github.com/encode/httpx --tag 0.27.0
uv add git+https://github.com/encode/httpx --branch main

# Add from local path
uv add ./packages/my-lib
uv add --editable ../projects/bar/

# Add from specific index
uv add torch --index pytorch=https://download.pytorch.org/whl/cpu

# Import from requirements.txt
uv add -r requirements.txt
```

### Removing Dependencies

```bash
uv remove requests
uv remove --dev pytest
uv remove --group lint ruff
```

### Upgrading Dependencies

```bash
# Upgrade specific package
uv lock --upgrade-package requests

# Upgrade all packages
uv lock --upgrade
```

### Syncing Environment

```bash
# Sync all dependencies (includes dev group by default)
uv sync

# Sync without dev dependencies
uv sync --no-dev

# Sync with frozen lockfile (CI use)
uv sync --frozen

# Sync specific groups
uv sync --group dev --group test

# Sync all groups
uv sync --all-groups
```

## Dependency Sources (tool.uv.sources)

### Workspace Member Source

```toml
[tool.uv.sources]
bird-feeder = { workspace = true }
```

### Git Source

```toml
[tool.uv.sources]
httpx = { git = "https://github.com/encode/httpx" }
httpx = { git = "https://github.com/encode/httpx", tag = "0.27.0" }
httpx = { git = "https://github.com/encode/httpx", branch = "main" }
httpx = { git = "https://github.com/encode/httpx", rev = "326b943" }
```

### Path Source

```toml
[tool.uv.sources]
foo = { path = "./packages/foo" }
bar = { path = "../projects/bar", editable = true }
```

### URL Source

```toml
[tool.uv.sources]
httpx = { url = "https://files.pythonhosted.org/.../httpx-0.27.0.tar.gz" }
```

### Index Source

```toml
[tool.uv.sources]
torch = { index = "pytorch" }

[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
explicit = true
```

### Platform-Specific Sources

```toml
[tool.uv.sources]
httpx = { git = "https://github.com/encode/httpx", tag = "0.27.2", marker = "sys_platform == 'darwin'" }
```

## Running Commands

### uv run

```bash
# Run Python script
uv run python script.py

# Run module
uv run python -m pytest

# Run project entry point (defined in project.scripts)
uv run commit-polish

# Run with extra dependencies (not added to project)
uv run --with httpx python script.py

# Run in specific package within workspace
uv run --package commit-polish pytest

# Run without project context
uv run --no-project python -c "print('hello')"

# Run with isolated environment
uv run --isolated python script.py
```

### Environment Activation (Alternative)

```bash
# Sync and activate manually
uv sync
source .venv/bin/activate  # Unix/macOS
.venv\Scripts\activate     # Windows

# Then run directly
python script.py
flask run -p 3000
```

## Scripts with Inline Dependencies (PEP 723)

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests>=2.28",
#     "rich",
# ]
# ///

import requests
from rich import print

response = requests.get("https://api.example.com")
print(response.json())
```

Run with:
```bash
uv run script.py
# or make executable and run directly
chmod +x script.py
./script.py
```

Add dependencies to existing script:
```bash
uv add --script example.py requests
```

## Tool Installation

### Install and Run Global Tools

```bash
# Install tool globally
uv tool install ruff

# Install with specific version
uv tool install "black>=24.0"

# Run without installing (ephemeral environment)
uvx ruff check .
uvx pycowsay 'hello world!'

# Equivalent to uvx
uv tool run ruff check .
```

## Dependency Groups (PEP 735)

```toml
[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.4",
]
test = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
]
docs = [
    "mkdocs>=1.6",
    "mkdocs-material>=9.0",
]

# Group inclusion
all = [
    { include-group = "dev" },
    { include-group = "test" },
    { include-group = "docs" },
]
```

### Default Groups Configuration

```toml
[tool.uv]
default-groups = ["dev", "test"]

# Or enable all groups by default
default-groups = "all"
```

## pyproject.toml Full Reference

```toml
[project]
name = "commit-polish"
version = "0.1.0"
description = "AI-powered commit message polisher"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.11"
authors = [
    { name = "Your Name", email = "you@example.com" }
]
keywords = ["git", "commit", "ai", "llm"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "litellm>=1.0.0",
    "tomlkit>=0.13.0",
]

[project.optional-dependencies]
network = ["httpx>=0.27"]

[project.scripts]
commit-polish = "commit_polish.hook:main"

[project.urls]
Homepage = "https://github.com/org/commit-polish"
Documentation = "https://commit-polish.readthedocs.io"
Repository = "https://github.com/org/commit-polish"

[build-system]
requires = ["uv_build>=0.9.2,<0.10.0"]
build-backend = "uv_build"

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "ruff>=0.4",
    "mypy>=1.10",
]

[tool.uv]
default-groups = ["dev"]

[tool.uv.workspace]
members = ["packages/*"]

[tool.uv.sources]
commit-polish-installer = { workspace = true }
```

## Common Commands Reference

| Command | Description |
|---------|-------------|
| `uv init` | Initialize new project |
| `uv init --lib` | Initialize as library |
| `uv init --package` | Initialize as distributable package |
| `uv add <pkg>` | Add dependency |
| `uv add --dev <pkg>` | Add dev dependency |
| `uv add --group <name> <pkg>` | Add to dependency group |
| `uv remove <pkg>` | Remove dependency |
| `uv sync` | Sync environment with lockfile |
| `uv sync --frozen` | Sync without updating lockfile |
| `uv lock` | Update lockfile |
| `uv lock --upgrade` | Upgrade all dependencies |
| `uv run <cmd>` | Run command in project environment |
| `uv run --package <name> <cmd>` | Run in specific workspace member |
| `uv build` | Build source and wheel distributions |
| `uv publish` | Publish to PyPI |
| `uv tool install <name>` | Install global tool |
| `uvx <tool>` | Run tool without installing |
| `uv python install 3.12` | Install Python version |
| `uv python list` | List available Python versions |
| `uv python pin 3.11` | Pin Python version for project |
| `uv version` | Show project version |
| `uv cache clean` | Clear cache |

## Testing Commands for commit-polish

```bash
# Run tests for specific package
cd packages/commit-polish
uv run pytest tests/

# Run tests from workspace root
uv run --package commit-polish pytest

# Run with coverage
uv run pytest --cov=commit_polish tests/

# Run linting
uv run ruff check src/ tests/

# Run type checking
uv run mypy src/

# Format code
uv run ruff format src/ tests/
```

## Building and Publishing

```bash
# Build package (creates dist/ directory)
uv build

# Build outputs
ls dist/
# example-0.1.0-py3-none-any.whl
# example-0.1.0.tar.gz

# Build specific package in workspace
cd packages/commit-polish && uv build

# Publish to PyPI
uv publish

# Publish with token
uv publish --token $PYPI_TOKEN

# Publish to test PyPI
uv publish --publish-url https://test.pypi.org/legacy/

# Smoke test before publishing
uv run --isolated --no-project --with dist/*.whl python -c "import commit_polish"
```

## GitHub Actions Integration

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v6

      - name: Set up Python
        run: uv python install 3.11

      - name: Install dependencies
        run: uv sync --frozen

      - name: Run tests
        run: uv run pytest

      - name: Build
        run: uv build

      # Cache for faster CI
      - uses: actions/cache@v4
        with:
          path: ~/.cache/uv
          key: uv-${{ runner.os }}-${{ hashFiles('uv.lock') }}
```

### Publishing Workflow

```yaml
name: Publish
on:
  push:
    tags:
      - v*

jobs:
  publish:
    runs-on: ubuntu-latest
    environment:
      name: pypi
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v5
      - uses: astral-sh/setup-uv@v6
      - run: uv python install 3.13
      - run: uv build
      - run: uv run --isolated --no-project --with dist/*.whl tests/smoke_test.py
      - run: uv publish  # Uses trusted publishing
```

## Integration with pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: commit-polish
        name: Polish Commit Message
        entry: uv run commit-polish
        language: system
        stages: [prepare-commit-msg]
        pass_filenames: false
        always_run: true
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `UV_CACHE_DIR` | Override cache location |
| `UV_NO_CACHE` | Disable caching |
| `UV_PYTHON` | Python interpreter to use |
| `UV_INDEX_URL` | Default package index |
| `UV_EXTRA_INDEX_URL` | Additional package indexes |
| `UV_LINK_MODE` | Install link mode |
| `UV_PUBLISH_TOKEN` | PyPI publish token |
| `UV_TOOL_DIR` | Override tool installation directory |
| `UV_PYTHON_INSTALL_DIR` | Override Python installation directory |

## Common Pitfalls

1. **Forgetting uv sync**: Run `uv sync` after cloning or after `uv add`
2. **Wrong workspace glob**: Use `packages/*` (with asterisk), not `packages/`
3. **Missing build-system**: Required for `--lib` and `--package` projects
4. **Text mode for TOML**: Use `'r'`/`'w'` with tomlkit (not binary mode)
5. **Workspace source syntax**: Use `{ workspace = true }` not `{ workspace = "true" }`
6. **Lockfile in CI**: Use `uv sync --frozen` to fail if lockfile is outdated
7. **Workspace requires-python**: All members must have compatible Python version ranges

## Version Information

- Build backend: `uv_build>=0.9.2,<0.10.0`
- Python support: 3.8+ (uv itself), project minimum set by `requires-python`
- Documentation last verified: 2025-05-18 (from docs.astral.sh)
