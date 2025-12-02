# XDG Base Directory Specification Reference

## Overview

The XDG Base Directory Specification defines where applications should store user-specific files. It standardizes configuration, data, cache, state, and runtime file locations across Linux and Unix systems.

**Specification Version**: 0.8 (Published: May 8, 2021)

**Authors**: Waldo Bastian, Allison Karlitskaya, Lennart Poettering, Johannes Löthberg

**Key Feature for commit-polish**: Configuration files are stored in `$XDG_CONFIG_HOME/commit-polish/` (default: `~/.config/commit-polish/`).

## Official Documentation

1. [XDG Base Directory Specification (freedesktop.org)](https://specifications.freedesktop.org/basedir-spec/latest/) - **Primary authoritative source**
2. [ArchWiki XDG Base Directory](https://wiki.archlinux.org/title/XDG_Base_Directory) - Comprehensive implementation guide
3. [Freedesktop.org Specifications Index](https://specifications.freedesktop.org/) - All freedesktop specifications
4. [XDG Specs Git Repository](https://cgit.freedesktop.org/xdg/xdg-specs/tree/basedir) - Source repository for the specification
5. [platformdirs Python Library](https://github.com/tox-dev/platformdirs) - Cross-platform Python implementation

## Environment Variables

### User-Specific Directories (Single Path)

| Variable | Purpose | Default |
|----------|---------|---------|
| `$XDG_CONFIG_HOME` | User configuration files | `$HOME/.config` |
| `$XDG_DATA_HOME` | User data files | `$HOME/.local/share` |
| `$XDG_STATE_HOME` | User state files (logs, history) | `$HOME/.local/state` |
| `$XDG_CACHE_HOME` | User cache files (non-essential) | `$HOME/.cache` |
| `$XDG_RUNTIME_DIR` | User runtime files (sockets, pipes) | Set by system (`/run/user/$UID`) |

### System-Wide Directories (Search Paths)

| Variable | Purpose | Default |
|----------|---------|---------|
| `$XDG_DATA_DIRS` | System data search path | `/usr/local/share/:/usr/share/` |
| `$XDG_CONFIG_DIRS` | System config search path | `/etc/xdg` |

### User Executables (Convention, not XDG)

| Path | Purpose |
|------|---------|
| `$HOME/.local/bin` | User-specific executable files |

**Note**: Distributions should ensure `$HOME/.local/bin` appears in `$PATH`.

## Directory Details

### XDG_CONFIG_HOME

**Purpose**: User-specific configuration files

**Default**: `$HOME/.config`

**Usage**: Application settings, preferences, user configurations

**commit-polish path**: `~/.config/commit-polish/config.toml`

### XDG_DATA_HOME

**Purpose**: User-specific data files

**Default**: `$HOME/.local/share`

**Usage**: Application data, databases, generated content that should persist

**commit-polish path**: `~/.local/share/commit-polish/models/` (for GGUF models)

### XDG_STATE_HOME

**Purpose**: User-specific state data that should persist between restarts but is not important or portable enough for `$XDG_DATA_HOME`

**Default**: `$HOME/.local/state`

**Usage per specification**:
- Action history (logs, history, recently used files)
- Current state of the application that can be reused on restart (view, layout, open files, undo history)

**Key distinction**: State differs from data in that it is less portable and can be regenerated or is non-essential.

### XDG_CACHE_HOME

**Purpose**: User-specific non-essential cached data

**Default**: `$HOME/.cache`

**Usage**: Temporary data, downloaded files that can be re-fetched, build artifacts

**commit-polish path**: `~/.cache/commit-polish/` (for temporary files)

### XDG_RUNTIME_DIR

**Purpose**: User-specific runtime files and file objects

**Default**: Set by system via `pam_systemd` (typically `/run/user/$UID`)

**Specification Requirements**:
- Must be owned by the user
- Access mode must be `0700` (user read/write/execute only)
- Must be on local filesystem (not NFS)
- Must support AF_UNIX sockets, symlinks, hard links, and file locking
- Created at login, removed at final logout
- Files may be cleaned periodically (applications should update access time every 6 hours or set sticky bit)
- Should not store large files (often tmpfs-mounted with size limits)

**Usage**: Sockets, named pipes, lock files, temporary IPC files

## Critical Specification Rules

From the official specification (Version 0.8):

### 1. Paths Must Be Absolute

> "All paths set in these environment variables must be absolute. If an implementation encounters a relative path in any of these variables it should consider the path invalid and ignore it."

### 2. Empty Variables Use Defaults

If a variable is not set or is empty, implementations must use the default value.

### 3. Priority Order

- User-specific directories (`$XDG_CONFIG_HOME`, `$XDG_DATA_HOME`) take precedence
- System directories (`$XDG_CONFIG_DIRS`, `$XDG_DATA_DIRS`) are searched in listed order
- First match wins

### 4. Colon Separator for DIRS Variables

`$XDG_DATA_DIRS` and `$XDG_CONFIG_DIRS` use colon (`:`) as path separator.

## Python Implementation

### Option 1: Pure Stdlib Implementation

```python
"""XDG Base Directory compliant path management using only stdlib."""
from pathlib import Path
import os


def get_config_home() -> Path:
    """Get XDG_CONFIG_HOME path.

    Returns the user-specific configuration directory.
    Falls back to $HOME/.config if not set.
    """
    xdg = os.environ.get('XDG_CONFIG_HOME')
    if xdg and Path(xdg).is_absolute():
        return Path(xdg)
    return Path.home() / '.config'


def get_data_home() -> Path:
    """Get XDG_DATA_HOME path.

    Returns the user-specific data directory.
    Falls back to $HOME/.local/share if not set.
    """
    xdg = os.environ.get('XDG_DATA_HOME')
    if xdg and Path(xdg).is_absolute():
        return Path(xdg)
    return Path.home() / '.local' / 'share'


def get_state_home() -> Path:
    """Get XDG_STATE_HOME path.

    Returns the user-specific state directory.
    Falls back to $HOME/.local/state if not set.
    """
    xdg = os.environ.get('XDG_STATE_HOME')
    if xdg and Path(xdg).is_absolute():
        return Path(xdg)
    return Path.home() / '.local' / 'state'


def get_cache_home() -> Path:
    """Get XDG_CACHE_HOME path.

    Returns the user-specific cache directory.
    Falls back to $HOME/.cache if not set.
    """
    xdg = os.environ.get('XDG_CACHE_HOME')
    if xdg and Path(xdg).is_absolute():
        return Path(xdg)
    return Path.home() / '.cache'


def get_runtime_dir() -> Path | None:
    """Get XDG_RUNTIME_DIR path.

    Returns the user-specific runtime directory, or None if not set.
    This variable has no default - it must be set by the system.
    """
    xdg = os.environ.get('XDG_RUNTIME_DIR')
    if xdg and Path(xdg).is_absolute():
        return Path(xdg)
    return None


def get_config_dirs() -> list[Path]:
    """Get XDG_CONFIG_DIRS as list of paths.

    Returns preference-ordered list of system configuration directories.
    Falls back to ['/etc/xdg'] if not set.
    """
    xdg = os.environ.get('XDG_CONFIG_DIRS')
    if xdg:
        paths = [Path(p) for p in xdg.split(':') if p and Path(p).is_absolute()]
        if paths:
            return paths
    return [Path('/etc/xdg')]


def get_data_dirs() -> list[Path]:
    """Get XDG_DATA_DIRS as list of paths.

    Returns preference-ordered list of system data directories.
    Falls back to ['/usr/local/share', '/usr/share'] if not set.
    """
    xdg = os.environ.get('XDG_DATA_DIRS')
    if xdg:
        paths = [Path(p) for p in xdg.split(':') if p and Path(p).is_absolute()]
        if paths:
            return paths
    return [Path('/usr/local/share'), Path('/usr/share')]
```

### Option 2: Using platformdirs Library (Recommended for Cross-Platform)

The `platformdirs` library provides cross-platform directory resolution with XDG support on Linux:

```python
"""Cross-platform path management using platformdirs."""
from platformdirs import user_config_dir, user_data_dir, user_cache_dir, user_state_dir
from pathlib import Path

APP_NAME = 'commit-polish'
APP_AUTHOR = 'commit-polish'  # Used on Windows

# Get platform-appropriate directories
# Linux: Uses XDG specification
# macOS: Uses ~/Library/Application Support, ~/Library/Caches, etc.
# Windows: Uses %APPDATA%, %LOCALAPPDATA%, etc.

config_dir = Path(user_config_dir(APP_NAME, APP_AUTHOR))
data_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))
cache_dir = Path(user_cache_dir(APP_NAME, APP_AUTHOR))
state_dir = Path(user_state_dir(APP_NAME, APP_AUTHOR))

# Example paths by platform:
# Linux:
#   config: ~/.config/commit-polish
#   data:   ~/.local/share/commit-polish
#   cache:  ~/.cache/commit-polish
#   state:  ~/.local/state/commit-polish
#
# macOS:
#   config: ~/Library/Application Support/commit-polish
#   data:   ~/Library/Application Support/commit-polish
#   cache:  ~/Library/Caches/commit-polish
#   state:  ~/Library/Application Support/commit-polish
#
# Windows:
#   config: C:\Users\<user>\AppData\Local\commit-polish\commit-polish
#   data:   C:\Users\<user>\AppData\Local\commit-polish\commit-polish
#   cache:  C:\Users\<user>\AppData\Local\commit-polish\commit-polish\Cache
#   state:  C:\Users\<user>\AppData\Local\commit-polish\commit-polish

# Auto-create directories
config_dir_auto = Path(user_config_dir(APP_NAME, APP_AUTHOR, ensure_exists=True))
```

### commit-polish Paths Module (Stdlib Only)

```python
"""Path management for commit-polish following XDG specification."""
from pathlib import Path
import os

APP_NAME = 'commit-polish'


def get_config_dir() -> Path:
    """Get commit-polish config directory."""
    xdg = os.environ.get('XDG_CONFIG_HOME')
    if xdg and Path(xdg).is_absolute():
        base = Path(xdg)
    else:
        base = Path.home() / '.config'
    return base / APP_NAME


def get_config_file() -> Path:
    """Get commit-polish config file path."""
    return get_config_dir() / 'config.toml'


def get_data_dir() -> Path:
    """Get commit-polish data directory (for models)."""
    xdg = os.environ.get('XDG_DATA_HOME')
    if xdg and Path(xdg).is_absolute():
        base = Path(xdg)
    else:
        base = Path.home() / '.local' / 'share'
    return base / APP_NAME


def get_models_dir() -> Path:
    """Get directory for LLM model files."""
    return get_data_dir() / 'models'


def get_cache_dir() -> Path:
    """Get commit-polish cache directory."""
    xdg = os.environ.get('XDG_CACHE_HOME')
    if xdg and Path(xdg).is_absolute():
        base = Path(xdg)
    else:
        base = Path.home() / '.cache'
    return base / APP_NAME


def get_state_dir() -> Path:
    """Get commit-polish state directory (for logs, history)."""
    xdg = os.environ.get('XDG_STATE_HOME')
    if xdg and Path(xdg).is_absolute():
        base = Path(xdg)
    else:
        base = Path.home() / '.local' / 'state'
    return base / APP_NAME


def ensure_directories() -> None:
    """Create all required directories with appropriate permissions."""
    for directory in [get_config_dir(), get_data_dir(), get_models_dir(),
                      get_cache_dir(), get_state_dir()]:
        directory.mkdir(parents=True, exist_ok=True)
```

## Directory Structure for commit-polish

```
~/.config/commit-polish/          # XDG_CONFIG_HOME
    config.toml                   # Main configuration

~/.local/share/commit-polish/     # XDG_DATA_HOME
    models/                       # LLM model files
        gemma-3-3b.gguf

~/.local/state/commit-polish/     # XDG_STATE_HOME
    history.log                   # Commit rewrite history (optional)

~/.local/bin/                     # User binaries (convention, not XDG)
    llamafile                     # Llamafile binary

~/.cache/commit-polish/           # XDG_CACHE_HOME
    (temporary files)
```

## Path Validation

```python
def validate_xdg_path(path_str: str | None) -> Path | None:
    """Validate XDG path is absolute per specification.

    Args:
        path_str: Environment variable value to validate

    Returns:
        Path object if valid, None if invalid or empty
    """
    if not path_str:
        return None
    path = Path(path_str)
    if not path.is_absolute():
        # Spec mandates ignoring relative paths
        return None
    return path
```

## Platform Considerations

### Linux

Full XDG support. Environment variables typically set by:
- `pam_systemd` for `XDG_RUNTIME_DIR`
- User shell configuration (`.bashrc`, `.zshrc`) for others
- Desktop environment session managers

### macOS

XDG is not native, but increasingly supported by CLI tools. Three approaches:

1. **XDG-first with macOS fallback** (recommended for CLI tools):
```python
def get_config_home_macos() -> Path:
    """Get config home with macOS fallback."""
    # Prefer XDG if explicitly set
    xdg = os.environ.get('XDG_CONFIG_HOME')
    if xdg and Path(xdg).is_absolute():
        return Path(xdg)
    # XDG default (preferred for CLI tools)
    return Path.home() / '.config'
```

2. **macOS-native** (for GUI apps):
```python
def get_config_home_macos_native() -> Path:
    """Get macOS native config location."""
    return Path.home() / 'Library' / 'Application Support'
```

3. **platformdirs** (automatic per-platform):
```python
from platformdirs import user_config_dir
config_dir = user_config_dir("commit-polish")
# Returns ~/Library/Application Support/commit-polish on macOS
```

### Windows

XDG is not native. Standard Windows locations:

| XDG Equivalent | Windows Variable | Typical Path |
|----------------|------------------|--------------|
| `XDG_CONFIG_HOME` | `%APPDATA%` | `C:\Users\<user>\AppData\Roaming` |
| `XDG_DATA_HOME` | `%LOCALAPPDATA%` | `C:\Users\<user>\AppData\Local` |
| `XDG_CACHE_HOME` | `%LOCALAPPDATA%\cache` | `C:\Users\<user>\AppData\Local\cache` |

```python
import platform

def get_config_home_cross_platform() -> Path:
    """Get config home across platforms."""
    if platform.system() == 'Windows':
        appdata = os.environ.get('APPDATA')
        if appdata:
            return Path(appdata)
        return Path.home() / 'AppData' / 'Roaming'

    # Unix-like (Linux, macOS, BSD)
    xdg = os.environ.get('XDG_CONFIG_HOME')
    if xdg and Path(xdg).is_absolute():
        return Path(xdg)
    return Path.home() / '.config'
```

## Common Pitfalls

1. **Using `~/.appname`**: Violates XDG spec; use `~/.config/appname/` instead
2. **Ignoring environment variables**: Always check `$XDG_*` before using defaults
3. **Accepting relative paths**: XDG mandates absolute paths; ignore relative ones
4. **Missing directory creation**: Always create directories before writing files
5. **Hardcoding paths**: Always use helper functions that respect XDG
6. **Storing cache in config**: Use `$XDG_CACHE_HOME` for regenerable data
7. **Large files in runtime dir**: `$XDG_RUNTIME_DIR` is often tmpfs with size limits
8. **Not handling unset `XDG_RUNTIME_DIR`**: This variable has no default; check for None

## Testing XDG Compliance

```bash
# Test with custom XDG directories
export XDG_CONFIG_HOME=/tmp/test-config
export XDG_DATA_HOME=/tmp/test-data
export XDG_CACHE_HOME=/tmp/test-cache
export XDG_STATE_HOME=/tmp/test-state

# Run application
commit-polish --help

# Verify files are in correct locations
ls -la /tmp/test-config/commit-polish/
ls -la /tmp/test-data/commit-polish/
ls -la /tmp/test-cache/commit-polish/
ls -la /tmp/test-state/commit-polish/

# Test with unset variables (should use defaults)
unset XDG_CONFIG_HOME XDG_DATA_HOME XDG_CACHE_HOME XDG_STATE_HOME
commit-polish --help
ls -la ~/.config/commit-polish/
```

## Python Testing Example

```python
"""Test XDG compliance."""
import os
import tempfile
from pathlib import Path

def test_xdg_config_home_override():
    """Test that XDG_CONFIG_HOME is respected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ['XDG_CONFIG_HOME'] = tmpdir
        try:
            config_dir = get_config_dir()
            assert config_dir == Path(tmpdir) / 'commit-polish'
        finally:
            del os.environ['XDG_CONFIG_HOME']

def test_xdg_config_home_default():
    """Test default when XDG_CONFIG_HOME is unset."""
    os.environ.pop('XDG_CONFIG_HOME', None)
    config_dir = get_config_dir()
    assert config_dir == Path.home() / '.config' / 'commit-polish'

def test_relative_path_ignored():
    """Test that relative paths in XDG variables are ignored."""
    os.environ['XDG_CONFIG_HOME'] = 'relative/path'
    try:
        config_dir = get_config_dir()
        # Should fall back to default, not use relative path
        assert config_dir == Path.home() / '.config' / 'commit-polish'
    finally:
        del os.environ['XDG_CONFIG_HOME']
```

## References

- **Official Specification**: https://specifications.freedesktop.org/basedir-spec/latest/
- **Wiki Homepage**: https://www.freedesktop.org/wiki/Specifications/basedir-spec/
- **Git Repository**: https://cgit.freedesktop.org/xdg/xdg-specs/tree/basedir
- **ArchWiki Guide**: https://wiki.archlinux.org/title/XDG_Base_Directory
- **platformdirs (Python)**: https://github.com/tox-dev/platformdirs
- **XDG Mailing List**: http://lists.freedesktop.org/mailman/listinfo/xdg
