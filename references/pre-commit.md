# Pre-commit Reference Documentation

## Overview

Pre-commit is a framework for managing and maintaining multi-language pre-commit hooks. It handles hook installation, environment management, and execution across git hook stages.

**Key Feature for commit-polish**: The `prepare-commit-msg` hook stage allows rewriting commit messages before they are finalized.

## Official Documentation URLs

| Resource | URL |
|----------|-----|
| Official Site | https://pre-commit.com/ |
| Creating New Hooks | https://pre-commit.com/#creating-new-hooks |
| Supported Git Hooks | https://pre-commit.com/#supported-git-hooks |
| Confining Hooks to Stages | https://pre-commit.com/#confining-hooks-to-run-at-certain-stages |
| Command Line Interface | https://pre-commit.com/#command-line-interface |
| GitHub Repository | https://github.com/pre-commit/pre-commit |
| Git prepare-commit-msg Docs | https://git-scm.com/docs/githooks#_prepare_commit_msg |

## Installation

```bash
# Using pip
pip install pre-commit

# Using uv
uv tool install pre-commit

# Verify installation
pre-commit --version
# Output: pre-commit 4.5.0
```

## Hook Stages (Verified from Official Documentation)

Pre-commit supports multiple git hook stages. The `stages` property values match the git hook names directly (as of pre-commit 3.2.0+).

| Stage | Description | Use Case |
|-------|-------------|----------|
| `pre-commit` | Before commit is created | Code formatting, linting |
| `prepare-commit-msg` | Before message editor opens | **Commit message rewriting** |
| `commit-msg` | After message is written | Message validation only |
| `pre-push` | Before push to remote | Tests, security checks |
| `pre-merge-commit` | Before merge commit (git 2.24+) | Merge validation |
| `post-checkout` | After checkout occurs | State setup |
| `post-commit` | After commit is created | Notifications |
| `post-merge` | After merge completes | Dependency updates |
| `post-rewrite` | After history modification | Amend/rebase handling |
| `pre-rebase` | Before rebase (3.2.0+) | Rebase validation |
| `manual` | Only via explicit invocation | On-demand tasks |

### prepare-commit-msg vs commit-msg (Critical Distinction)

| Feature | prepare-commit-msg | commit-msg |
|---------|-------------------|------------|
| **Purpose** | Modify message content | Validate final message |
| **Can modify message** | **Yes** | No (validation only) |
| **Hook receives** | Message file path | Message file path |
| **Environment variables** | `PRE_COMMIT_COMMIT_MSG_SOURCE`, `PRE_COMMIT_COMMIT_OBJECT_NAME` | None |
| **When it runs** | Before editor opens | After message is written |
| **Abort on non-zero** | Yes | Yes |

**For commit-polish**: Use `prepare-commit-msg` because we need to **rewrite** the message, not just validate it.

> **Source**: [git prepare-commit-msg docs](https://git-scm.com/docs/githooks#_prepare_commit_msg) - "prepare-commit-msg hooks will be passed a single filename -- this file may be empty or it could contain the commit message from `-m` or from other templates. prepare-commit-msg hooks can modify the contents of this file to change what will be committed."

## Configuration Files

### .pre-commit-config.yaml (User Config)

This file is placed in the user's repository root to configure which hooks to use.

#### Top-Level Schema

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `repos` | list | Required | List of repository mappings |
| `default_install_hook_types` | list | `[pre-commit]` | Hook types installed by default with `pre-commit install` |
| `default_language_version` | map | `{}` | Default language versions for hooks |
| `default_stages` | list | all stages | Default stages for hooks without explicit `stages` |
| `files` | regex | `''` | Global file include pattern |
| `exclude` | regex | `^$` | Global file exclude pattern |
| `fail_fast` | bool | `false` | Stop on first hook failure |
| `minimum_pre_commit_version` | string | `'0'` | Minimum pre-commit version required |

#### Repository Mapping Schema

| Property | Type | Description |
|----------|------|-------------|
| `repo` | string | Repository URL or `local` / `meta` sentinel |
| `rev` | string | Revision or tag to clone (immutable ref recommended) |
| `hooks` | list | List of hook configurations |

#### Hook Configuration Schema (in .pre-commit-config.yaml)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `id` | string | Required | Hook ID from repository |
| `alias` | string | - | Alternative ID for `pre-commit run` |
| `name` | string | - | Override display name |
| `language_version` | string | - | Override language version |
| `files` | regex | - | Override file pattern |
| `exclude` | regex | - | File exclude pattern |
| `types` | list | - | File types to match (AND logic) |
| `types_or` | list | - | File types to match (OR logic) |
| `exclude_types` | list | - | File types to exclude |
| `args` | list | - | Additional arguments to pass |
| `stages` | list | - | Override hook stages |
| `additional_dependencies` | list | - | Extra dependencies to install |
| `always_run` | bool | - | Run even without matching files |
| `verbose` | bool | - | Force output even on success |
| `log_file` | string | - | File path for hook output |

#### Example: commit-polish User Configuration

```yaml
# .pre-commit-config.yaml in user's repository
repos:
  - repo: https://github.com/your-org/commit-polish
    rev: v1.0.0
    hooks:
      - id: commit-polish
        stages: [prepare-commit-msg]
```

### .pre-commit-hooks.yaml (Hook Definition)

This file is placed in the hook repository to define available hooks.

#### Hook Definition Schema (Verified from Official Docs)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `id` | string | **Required** | Unique hook identifier |
| `name` | string | **Required** | Display name during execution |
| `entry` | string | **Required** | Command to execute (can include args) |
| `language` | string | **Required** | Hook language (python, node, etc.) |
| `files` | regex | `''` | Pattern of files to run on |
| `exclude` | regex | `^$` | Pattern to exclude from `files` |
| `types` | list | `[file]` | File types to run on (AND logic) |
| `types_or` | list | `[]` | File types to run on (OR logic) |
| `exclude_types` | list | `[]` | File types to exclude |
| `always_run` | bool | `false` | Run even without matching files |
| `fail_fast` | bool | `false` | Stop pre-commit on this hook's failure |
| `verbose` | bool | `false` | Force output even on success |
| `pass_filenames` | bool | `true` | Pass staged files to hook |
| `require_serial` | bool | `false` | Force sequential execution |
| `description` | string | `''` | Hook description (metadata only) |
| `language_version` | string | `default` | Language version to use |
| `minimum_pre_commit_version` | string | `'0'` | Minimum pre-commit version |
| `args` | list | `[]` | Default arguments |
| `stages` | list | all stages | Git hooks to run for |

#### Example: commit-polish Hook Definition

```yaml
# .pre-commit-hooks.yaml in commit-polish repository
- id: commit-polish
  name: Polish Commit Message
  description: Rewrites commit messages using local LLM
  entry: commit-polish
  language: python
  stages: [prepare-commit-msg]  # MUST be prepare-commit-msg for message rewriting
  pass_filenames: false         # Hook receives message file path, not staged files
  always_run: true              # Run even without file changes
```

## Hook Arguments for prepare-commit-msg

### What the Hook Receives

The `prepare-commit-msg` hook receives:

1. **Positional argument** (`sys.argv[1]`): Path to the commit message file (e.g., `.git/COMMIT_EDITMSG`)

2. **Environment variables** (set by pre-commit framework):
   - `PRE_COMMIT_COMMIT_MSG_SOURCE`: The source of the commit message:
     - `message` - from `-m` flag
     - `template` - from template file
     - `merge` - from merge operation
     - `squash` - from squash operation
     - `commit` - from existing commit (amend)
   - `PRE_COMMIT_COMMIT_OBJECT_NAME`: Commit SHA (for amend operations)

### Copy-Paste Ready Hook Implementation

```python
#!/usr/bin/env python3
"""commit-polish hook entry point for prepare-commit-msg stage."""
import os
import sys


def main() -> int:
    """Entry point for pre-commit hook.

    Returns:
        0 on success, non-zero aborts the commit.
    """
    if len(sys.argv) < 2:
        print("Error: No commit message file provided", file=sys.stderr)
        return 1

    # Get commit message file path from pre-commit
    commit_msg_file = sys.argv[1]  # e.g., .git/COMMIT_EDITMSG

    # Get optional environment info
    source = os.environ.get('PRE_COMMIT_COMMIT_MSG_SOURCE', '')
    commit_sha = os.environ.get('PRE_COMMIT_COMMIT_OBJECT_NAME', '')

    # Read current message
    with open(commit_msg_file, encoding='utf-8') as f:
        original_message = f.read()

    # Skip if message is empty or just whitespace
    if not original_message.strip():
        return 0

    # Process message (your rewriting logic here)
    new_message = process_commit_message(original_message)

    # Write back the modified message
    with open(commit_msg_file, 'w', encoding='utf-8') as f:
        f.write(new_message)

    return 0  # Success - commit proceeds


def process_commit_message(message: str) -> str:
    """Transform the commit message.

    Args:
        message: Original commit message

    Returns:
        Transformed commit message
    """
    # Your LLM rewriting logic here
    return message


if __name__ == "__main__":
    sys.exit(main())
```

### pyproject.toml Entry Point Configuration

```toml
[project.scripts]
commit-polish = "commit_polish.hook:main"
```

## Installation Commands

### Install Hooks in a Repository

```bash
# Install default hook type (pre-commit stage only)
pre-commit install

# Install specific hook type - REQUIRED for prepare-commit-msg
pre-commit install --hook-type prepare-commit-msg

# Install multiple hook types
pre-commit install --hook-type pre-commit --hook-type prepare-commit-msg

# Install and setup environments immediately
pre-commit install --install-hooks

# Overwrite existing hooks
pre-commit install --overwrite

# Allow missing config (useful for templates)
pre-commit install --allow-missing-config
```

### Configure Default Hook Types

To automatically install `prepare-commit-msg` hooks with `pre-commit install`:

```yaml
# .pre-commit-config.yaml
default_install_hook_types: [pre-commit, prepare-commit-msg]
```

Then a simple `pre-commit install` will install both hook types.

### Running Hooks Manually

```bash
# Run all hooks for default stage
pre-commit run

# Run specific hook
pre-commit run commit-polish

# Run specific hook stage
pre-commit run --hook-stage prepare-commit-msg

# Run on all files (for pre-commit stage hooks)
pre-commit run --all-files

# Test hook with verbose output
pre-commit run commit-polish --verbose
```

### Testing prepare-commit-msg Hooks

**Note**: When using `pre-commit try-repo` with `prepare-commit-msg` or `commit-msg` hooks, you may need to provide `--commit-msg-filename`.

```bash
# Test hook from local repo
pre-commit try-repo /path/to/commit-polish commit-polish --verbose \
    --commit-msg-filename .git/COMMIT_EDITMSG

# Test hook from remote
pre-commit try-repo https://github.com/your-org/commit-polish commit-polish
```

### Test prepare-commit-msg Hook Manually (Without pre-commit)

```bash
# Create test message file
echo "fix bug" > /tmp/test-commit-msg

# Run hook directly
python -m commit_polish.hook /tmp/test-commit-msg

# Check result
cat /tmp/test-commit-msg
```

## Environment Variables

### Skip Specific Hooks

```bash
# Skip specific hook
SKIP=commit-polish git commit -m "message"

# Skip multiple hooks
SKIP=commit-polish,trailing-whitespace git commit -m "message"
```

### Disable All Hooks

```bash
# Skip all pre-commit hooks
git commit --no-verify -m "message"
```

### Cache Location

```bash
# Default: ~/.cache/pre-commit
# Override with:
export PRE_COMMIT_HOME=/custom/path

# Or use XDG spec:
export XDG_CACHE_HOME=/custom/cache
# Results in: /custom/cache/pre-commit
```

## Common Pitfalls to Avoid

1. **Using `commit-msg` stage for rewriting**: Use `prepare-commit-msg` for modification, `commit-msg` for validation only.

2. **Setting `pass_filenames: true`** with commit-msg stages: These stages receive the message file path as an argument, not staged files. Set `pass_filenames: false`.

3. **Forgetting `always_run: true`**: Without this, hook may be skipped if no files match the `files`/`types` patterns.

4. **Wrong hook stage installation**: Must use `pre-commit install --hook-type prepare-commit-msg` explicitly, or set `default_install_hook_types`.

5. **Non-zero exit aborting commit**: Return 0 for success, any non-zero exit code aborts the commit.

6. **Using mutable refs for `rev`**: Always use immutable refs (tags or SHAs) for `rev`. Branch names won't auto-update.

7. **Missing `--commit-msg-filename` in try-repo**: When testing `prepare-commit-msg` hooks with `try-repo`, provide this flag.

## Complete Example: commit-polish Integration

### Hook Repository Structure

```
commit-polish/
├── .pre-commit-hooks.yaml      # Hook definition
├── pyproject.toml              # Package config with entry point
└── src/
    └── commit_polish/
        ├── __init__.py
        └── hook.py             # Hook entry point
```

### .pre-commit-hooks.yaml

```yaml
- id: commit-polish
  name: Polish Commit Message
  description: Rewrites commit messages to conventional commits format using local LLM
  entry: commit-polish
  language: python
  stages: [prepare-commit-msg]
  pass_filenames: false
  always_run: true
  minimum_pre_commit_version: '3.2.0'
```

### User's .pre-commit-config.yaml

```yaml
# Minimum recommended config
default_install_hook_types: [pre-commit, prepare-commit-msg]

repos:
  # Standard code quality hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml

  # Commit message polishing
  - repo: https://github.com/your-org/commit-polish
    rev: v1.0.0
    hooks:
      - id: commit-polish
        stages: [prepare-commit-msg]
```

### Installation Flow

```bash
# In user's repository
cd /path/to/user-repo

# Install all configured hook types
pre-commit install
# Output:
# pre-commit installed at .git/hooks/pre-commit
# pre-commit installed at .git/hooks/prepare-commit-msg

# Make a commit - hook runs automatically
git add .
git commit -m "fix bug"
# Hook rewrites message before editor opens (if configured)
```

## Version Compatibility

| Component | Minimum Version | Notes |
|-----------|-----------------|-------|
| pre-commit | 3.2.0 | Stage values match hook names |
| Python | 3.8+ | For pre-commit framework |
| Git | 2.24+ | Required for `pre-merge-commit` stage |

## References

- [Pre-commit Official Documentation](https://pre-commit.com/)
- [Git Hooks Documentation](https://git-scm.com/docs/githooks)
- [Pre-commit GitHub Repository](https://github.com/pre-commit/pre-commit)
- [Creating New Hooks Guide](https://pre-commit.com/#creating-new-hooks)
- [Supported Git Hooks](https://pre-commit.com/#supported-git-hooks)
