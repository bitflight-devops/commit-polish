# TOML Python Libraries Reference Documentation

## Overview

TOML (Tom's Obvious Minimal Language) is a configuration file format used extensively in Python packaging (`pyproject.toml`). For **commit-polish**, we use `tomlkit` - a library that combines read and write functionality while preserving comments and formatting.

**Key Feature for commit-polish**: Configuration is stored in TOML format at `~/.config/commit-polish/config.toml`.

## Why tomlkit?

For **commit-polish**, we recommend `tomlkit` because:

1. **Single library for read/write**: No need for separate `tomllib` + `tomli_w`
2. **Comment preservation**: Comments in config files survive read-modify-write cycles
3. **Format preservation**: Original indentation and formatting are maintained
4. **Cleaner API**: Simpler, more intuitive syntax for nested structures
5. **Production-ready**: Used in major projects like Poetry for TOML manipulation
6. **TOML 1.0.0 compliant**: Full compliance with the TOML specification

### Alternative: tomllib (stdlib, read-only)

Python 3.11+ includes `tomllib` for reading TOML (read-only). For **commit-polish**, this is insufficient because we need to modify config files during setup. If you only need reading, see the [stdlib documentation](https://docs.python.org/3.11/library/tomllib.html).

## Official Documentation

- **API Reference**: [https://tomlkit.readthedocs.io/en/latest/api/](https://tomlkit.readthedocs.io/en/latest/api/)
- **Quickstart Guide**: [https://tomlkit.readthedocs.io/en/latest/quickstart/](https://tomlkit.readthedocs.io/en/latest/quickstart/)
- **PyPI Package**: [https://pypi.org/project/tomlkit/](https://pypi.org/project/tomlkit/)
- **GitHub Repository**: [https://github.com/sdispater/tomlkit](https://github.com/sdispater/tomlkit)
- **TOML Specification**: [https://toml.io/en/](https://toml.io/en/)

## tomlkit Installation

```bash
# Using pip
pip install tomlkit

# Using uv (recommended for this project)
uv add tomlkit
```

**Requirements**: Python >=3.8 (per PyPI metadata). Current version: 0.13.3 (released June 5, 2025).

## tomlkit API Reference

### Core Parsing Functions

#### tomlkit.parse()

```python
tomlkit.parse(string: str | bytes) -> TOMLDocument
```

Parses a string or bytes into a TOMLDocument.

**Parameters**:
- `string`: String or bytes containing valid TOML

**Returns**: `TOMLDocument` instance that preserves comments and formatting

**Raises**: `tomlkit.exceptions.ParseError` for invalid TOML syntax

**Example**:
```python
from tomlkit import parse

doc = parse("""
[table]
foo = "bar"  # String
""")
assert doc["table"]["foo"] == "bar"
```

#### tomlkit.loads()

```python
tomlkit.loads(string: str | bytes) -> TOMLDocument
```

Alias for `parse()`. Parses a string or bytes into a TOMLDocument.

#### tomlkit.load()

```python
tomlkit.load(fp: IO[str] | IO[bytes]) -> TOMLDocument
```

Load a TOML document from a file-like object.

**Parameters**:
- `fp`: File object opened in text mode (`'r'`) or binary mode (`'rb'`)

**Returns**: `TOMLDocument` instance preserving formatting

**Example**:
```python
import tomlkit

# Text mode
with open('config.toml', 'r') as f:
    config = tomlkit.load(f)

# Binary mode also supported
with open('config.toml', 'rb') as f:
    config = tomlkit.load(f)
```

### Core Writing Functions

#### tomlkit.dump()

```python
tomlkit.dump(data: Mapping, fp: IO[str], *, sort_keys: bool = False) -> None
```

Dump a TOMLDocument into a writable file stream.

**Parameters**:
- `data`: A dict-like object to dump
- `fp`: File object opened for writing (text mode)
- `sort_keys`: If true, sort the keys in alphabetic order

**Example**:
```python
import tomlkit

config = tomlkit.parse("[ai]\nmodel = 'test'")
with open("output.toml", "w") as fp:
    tomlkit.dump(config, fp)
```

#### tomlkit.dumps()

```python
tomlkit.dumps(data: Mapping, sort_keys: bool = False) -> str
```

Dumps a TOMLDocument into a string.

**Parameters**:
- `data`: A dict-like object to dump
- `sort_keys`: If true, sort the keys in alphabetic order

**Returns**: `str` - TOML formatted string

**Example**:
```python
import tomlkit

config = {"ai": {"model": "llamafile/gemma-3-3b"}}
toml_string = tomlkit.dumps(config)
```

### Document Creation Functions

#### tomlkit.document()

```python
tomlkit.document() -> TOMLDocument
```

Returns a new TOMLDocument instance for building TOML from scratch.

**Example**:
```python
from tomlkit import document, table

doc = document()
doc.add("title", "TOML Example")
doc["database"] = table()
doc["database"]["server"] = "192.168.1.1"
```

#### tomlkit.table()

```python
tomlkit.table(is_super_table: bool | None = None) -> Table
```

Create an empty table.

**Parameters**:
- `is_super_table`: If true, the table is a super table (intermediate parent of nested tables)

**Example**:
```python
from tomlkit import document, table

doc = document()
foo = table(True)  # Super table
bar = table()
bar.update({'x': 1})
foo.append('bar', bar)
doc.append('foo', foo)
print(doc.as_string())
# [foo.bar]
# x = 1
```

#### tomlkit.inline_table()

```python
tomlkit.inline_table() -> InlineTable
```

Create an inline table.

**Example**:
```python
from tomlkit import inline_table

tbl = inline_table()
tbl.update({'x': 1, 'y': 2})
print(tbl.as_string())
# {x = 1, y = 2}
```

#### tomlkit.array()

```python
tomlkit.array(raw: str = '[]') -> Array
```

Create an array item from its string representation.

**Example**:
```python
from tomlkit import array

a = array("[1, 2, 3]")  # Create from a string
# Or create empty and extend
a = array()
a.extend([1, 2, 3])
```

#### tomlkit.aot()

```python
tomlkit.aot() -> AoT
```

Create an array of tables.

**Example**:
```python
from tomlkit import document, aot, item

doc = document()
products = aot()
products.append(item({'name': 'Widget', 'price': 9.99}))
products.append(item({'name': 'Gadget', 'price': 19.99}))
doc.append('products', products)
print(doc.as_string())
# [[products]]
# name = "Widget"
# price = 9.99
#
# [[products]]
# name = "Gadget"
# price = 19.99
```

### Value Creation Functions

#### tomlkit.item()

```python
tomlkit.item(value: Any, _parent: Item | None = None, _sort_keys: bool = False) -> Item
```

Create a TOML item from a Python object.

**Example**:
```python
from tomlkit import item

item(42)           # Integer
item([1, 2, 3])    # Array
item({'a': 1})     # Table
```

#### tomlkit.value()

```python
tomlkit.value(raw: str) -> Item
```

Parse a simple value from a string.

**Example**:
```python
from tomlkit import value

value("1")           # Integer: 1
value("true")        # Boolean: True
value("[1, 2, 3]")   # Array: [1, 2, 3]
```

#### tomlkit.string()

```python
tomlkit.string(raw: str, *, literal: bool = False, multiline: bool = False, escape: bool = True) -> String
```

Create a string item with control over string type.

**Parameters**:
- `raw`: The string content
- `literal`: Use literal string (single quotes) instead of basic string (double quotes)
- `multiline`: Create a multiline string
- `escape`: Apply common escaping rules (only for basic strings)

#### tomlkit.integer()

```python
tomlkit.integer(raw: str | int) -> Integer
```

Create an integer item from a number or string.

#### tomlkit.float_()

```python
tomlkit.float_(raw: str | float) -> Float
```

Create a float item from a number or string.

#### tomlkit.boolean()

```python
tomlkit.boolean(raw: str) -> Bool
```

Turn "true" or "false" into a boolean item.

#### tomlkit.datetime()

```python
tomlkit.datetime(raw: str) -> DateTime
```

Create a TOML datetime from an RFC 3339 string.

#### tomlkit.date()

```python
tomlkit.date(raw: str) -> Date
```

Create a TOML date.

#### tomlkit.time()

```python
tomlkit.time(raw: str) -> Time
```

Create a TOML time.

### Formatting Functions

#### tomlkit.comment()

```python
tomlkit.comment(string: str) -> Comment
```

Create a comment item.

**Example**:
```python
from tomlkit import document, comment, nl

doc = document()
doc.add(comment("This is a TOML document."))
doc.add(nl())
doc.add("title", "Example")
```

#### tomlkit.nl()

```python
tomlkit.nl() -> Whitespace
```

Create a newline item.

#### tomlkit.ws()

```python
tomlkit.ws(src: str) -> Whitespace
```

Create a whitespace item from a string.

#### tomlkit.key()

```python
tomlkit.key(k: str | Iterable[str]) -> Key
```

Create a key from a string. When a list of strings is given, it creates a dotted key.

**Example**:
```python
from tomlkit import document, key

doc = document()
doc.append(key('foo'), 1)
doc.append(key(['bar', 'baz']), 2)
print(doc.as_string())
# foo = 1
# bar.baz = 2
```

#### tomlkit.key_value()

```python
tomlkit.key_value(src: str) -> tuple[Key, Item]
```

Parse a key-value pair from a string.

**Example**:
```python
from tomlkit import key_value

k, v = key_value("foo = 1")
# k is Key('foo'), v is 1
```

### Custom Encoders

#### tomlkit.register_encoder()

```python
tomlkit.register_encoder(encoder: E) -> E
```

Add a custom encoder function that will be called if a value can't otherwise be converted. The encoder should take a single value and return a TOMLKit item or raise a `ConvertError`.

#### tomlkit.unregister_encoder()

```python
tomlkit.unregister_encoder(encoder: Encoder) -> None
```

Unregister a custom encoder.

## TOMLDocument Class

```python
class tomlkit.TOMLDocument(parsed: bool = False)
```

A TOML document. Inherits from `Container` and behaves like a standard dictionary.

### Key Methods

| Method | Description |
|--------|-------------|
| `add(key, item)` | Add a key-value pair or formatting element (comment, whitespace) |
| `append(key, item)` | Similar to `add()` but both key and value must be given |
| `as_string()` | Render as TOML string |
| `item(key)` | Get an Item for the given key |
| `remove(key)` | Remove a key from the container |
| `unwrap()` | Returns as pure Python object (dict) |
| `copy()` | Return a shallow copy |
| `clear()` | Remove all items |
| `get(key, default)` | Get value with optional default |
| `keys()` | Return view of keys |
| `values()` | Return view of values |
| `items()` | Return view of items |
| `update(mapping)` | Update from mapping or iterable |
| `pop(key, default)` | Remove and return value |
| `setdefault(key, default)` | Get or set default value |
| `last_item()` | Get the last item |

**Example**:
```python
from tomlkit import parse

doc = parse("[ai]\nmodel = 'test'")

# Dict-like access
doc["ai"]["model"] = "new_model"

# Get as string
print(doc.as_string())

# Get as pure Python dict
pure_dict = doc.unwrap()
```

## TOMLFile Class

```python
class tomlkit.TOMLFile(path: str | PathLike)
```

Represents a TOML file for convenient read/write operations.

**Parameters**:
- `path`: Path to the TOML file

### Methods

| Method | Description |
|--------|-------------|
| `read()` | Read the file content as a `TOMLDocument` |
| `write(data)` | Write the TOMLDocument to the file |

**Example**:
```python
from tomlkit import TOMLFile

# Using TOMLFile for convenient file operations
toml_file = TOMLFile("config.toml")

# Read
config = toml_file.read()

# Modify
config["ai"]["temperature"] = 0.5

# Write back
toml_file.write(config)
```

## Exception Types

All exceptions are in `tomlkit.exceptions`:

### Base Exception

```python
class tomlkit.exceptions.TOMLKitError(Exception)
```

Base class for all tomlkit errors.

### Parse Errors

```python
class tomlkit.exceptions.ParseError(ValueError, TOMLKitError)
```

Raised when the parser encounters a syntax error. Contains `line` and `col` attributes indicating the error location.

**Attributes**:
- `line`: Line number where error occurred
- `col`: Column number where error occurred

**Subclasses**:
- `EmptyKeyError` - An empty key was found
- `EmptyTableNameError` - An empty table name was found
- `UnexpectedCharError` - An unexpected character was found
- `UnexpectedEofError` - TOML ended before end of statement
- `InvalidNumberError` - A numeric field was improperly specified
- `InvalidDateError` - A date field was improperly specified
- `InvalidTimeError` - A time field was improperly specified
- `InvalidDateTimeError` - A datetime field was improperly specified
- `InvalidUnicodeValueError` - A unicode code was improperly specified
- `InvalidCharInStringError` - String contains an invalid character
- `InvalidControlChar` - Invalid control character in string
- `InvalidNumberOrDateError` - A numeric or date field was improperly specified
- `MixedArrayTypesError` - An array had mixed element types
- `InternalParserError` - Indicates a bug in the parser

### Value Errors

```python
class tomlkit.exceptions.ConvertError(TypeError, ValueError, TOMLKitError)
```

Raised when `item()` fails to convert a value.

```python
class tomlkit.exceptions.InvalidStringError(ValueError, TOMLKitError)
```

Raised when a string contains invalid sequences.

### Key Errors

```python
class tomlkit.exceptions.KeyAlreadyPresent(TOMLKitError)
```

Raised when attempting to add a key that already exists.

```python
class tomlkit.exceptions.NonExistentKey(KeyError, TOMLKitError)
```

Raised when accessing a key that doesn't exist.

## Error Handling Examples

```python
import tomlkit
from tomlkit.exceptions import ParseError, NonExistentKey

# Handle parse errors
try:
    config = tomlkit.parse("invalid = [toml")
except ParseError as e:
    print(f"Parse error at line {e.line}, column {e.col}: {e}")

# Handle file not found
try:
    with open('config.toml', 'r') as f:
        config = tomlkit.load(f)
except FileNotFoundError:
    print("Config file not found")
except ParseError as e:
    print(f"Invalid TOML: {e}")

# Handle missing keys
try:
    value = config["nonexistent"]["key"]
except (KeyError, NonExistentKey):
    print("Key not found")
```

## Usage Examples

### Reading a TOML File

```python
import tomlkit
from pathlib import Path

config_path = Path.home() / '.config' / 'commit-polish' / 'config.toml'

with open(config_path, 'r') as f:
    config = tomlkit.load(f)

print(config['ai']['model'])
print(config['llamafile']['path'])
```

### Parsing a TOML String

```python
import tomlkit

toml_string = """
[ai]
model = "llamafile/gemma-3-3b"
temperature = 0.3
max_tokens = 200

[llamafile]
path = "/home/user/.local/bin/llamafile"

[validation]
auto_detect = true
max_retries = 3
"""

config = tomlkit.parse(toml_string)
print(config['ai']['temperature'])
```

### Writing to a TOML File

```python
import tomlkit
from pathlib import Path

config = {
    'ai': {
        'model': 'llamafile/gemma-3-3b',
        'temperature': 0.3,
        'max_tokens': 200,
    },
    'llamafile': {
        'path': '/home/user/.local/bin/llamafile',
        'model_path': '/home/user/.local/share/commit-polish/models/gemma-3-3b.gguf',
    },
    'validation': {
        'auto_detect': True,
        'max_retries': 3,
    },
}

config_path = Path.home() / '.config' / 'commit-polish' / 'config.toml'
config_path.parent.mkdir(parents=True, exist_ok=True)

with open(config_path, 'w') as f:
    tomlkit.dump(config, f)
```

### Comment Preservation (Key Advantage)

This is where tomlkit excels - comments survive modification cycles:

```python
import tomlkit

original_toml = """
# Configuration for commit-polish
[ai]
# Model to use for rewriting commits
model = "llamafile/gemma-3-3b"
# Temperature for generation (0.0-1.0)
temperature = 0.3
"""

# Parse preserving comments
config = tomlkit.parse(original_toml)

# Modify values
config['ai']['temperature'] = 0.5

# Dump - comments are still there!
result = tomlkit.dumps(config)
print(result)
# Output preserves all comments:
# # Configuration for commit-polish
# [ai]
# # Model to use for rewriting commits
# model = "llamafile/gemma-3-3b"
# # Temperature for generation (0.0-1.0)
# temperature = 0.5
```

### Creating Documents Programmatically

```python
from tomlkit import document, table, comment, nl
from datetime import datetime, timezone

doc = document()
doc.add(comment("This is a TOML document."))
doc.add(nl())
doc.add("title", "TOML Example")

# Add a table with values
owner = table()
owner.add("name", "Tom Preston-Werner")
owner.add("organization", "GitHub")
owner.add("dob", datetime(1979, 5, 27, 7, 32, tzinfo=timezone.utc))
owner["dob"].comment("First class dates? Why not?")
doc.add("owner", owner)

# Add another table using dict-like syntax
database = table()
database["server"] = "192.168.1.1"
database["ports"] = [8001, 8001, 8002]
database["connection_max"] = 5000
database["enabled"] = True
doc["database"] = database

print(doc.as_string())
```

### Using TOMLFile Class

```python
from tomlkit import TOMLFile
from pathlib import Path

config_path = Path.home() / '.config' / 'commit-polish' / 'config.toml'

# Create TOMLFile instance
toml_file = TOMLFile(config_path)

# Read existing config
config = toml_file.read()

# Modify
config['ai']['temperature'] = 0.7

# Write back (preserves comments and formatting)
toml_file.write(config)
```

### Working with Arrays

```python
from tomlkit import array, document

doc = document()

# Create array with formatted output
a = array()
a.add_line(1, 2, 3)
a.add_line(4, 5, 6)
a.add_line(indent="")

doc["numbers"] = a
print(doc.as_string())
# numbers = [
#     1, 2, 3,
#     4, 5, 6,
# ]

# Multiline array
from tomlkit import item
arr = item([1, 2, 3])
print(arr.multiline(True).as_string())
# [
#     1,
#     2,
#     3,
# ]
```

### Inline Tables

```python
from tomlkit import document, inline_table

doc = document()

point = inline_table()
point.update({'x': 1, 'y': 2, 'z': 3})

doc["point"] = point
print(doc.as_string())
# point = {x = 1, y = 2, z = 3}
```

## Complete commit-polish Config Example

### Configuration File Format

```toml
# ~/.config/commit-polish/config.toml
# Generated by commit-polish-installer

[ai]
# Model to use for rewriting commit messages
model = "llamafile/gemma-3-3b"
# Temperature for generation (0.0 = deterministic, 1.0 = creative)
temperature = 0.3
# Maximum tokens in generated message
max_tokens = 200

[llamafile]
# Path to llamafile binary
path = "/home/user/.local/bin/llamafile"
# Path to GGUF model file
model_path = "/home/user/.local/share/commit-polish/models/gemma-3-3b.gguf"

[validation]
# Auto-detect commitlint, semantic-release, commitizen configs
auto_detect = true
# Maximum retry attempts if validation fails
max_retries = 3
# Optional: Custom validator command (uncomment to use)
# validator_command = "npx commitlint --from HEAD~1"
# Optional: Custom system prompt (uncomment to override default)
# system_prompt = "Your custom instructions here"
```

### Python Config Management with tomlkit

```python
"""Configuration management for commit-polish using tomlkit."""
import tomlkit
from tomlkit import TOMLFile
from tomlkit.exceptions import ParseError, NonExistentKey
from pathlib import Path
from dataclasses import dataclass

@dataclass
class AIConfig:
    model: str = "llamafile/gemma-3-3b"
    temperature: float = 0.3
    max_tokens: int = 200

@dataclass
class LlamafileConfig:
    path: str = ""
    model_path: str = ""

@dataclass
class ValidationConfig:
    auto_detect: bool = True
    max_retries: int = 3
    validator_command: str | None = None
    system_prompt: str | None = None

@dataclass
class Config:
    ai: AIConfig
    llamafile: LlamafileConfig
    validation: ValidationConfig

def load_config(path: Path) -> Config:
    """Load configuration from TOML file."""
    try:
        with open(path, 'r') as f:
            data = tomlkit.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {path}")
    except ParseError as e:
        raise ValueError(f"Invalid TOML at line {e.line}: {e}")

    return Config(
        ai=AIConfig(**data.get('ai', {})),
        llamafile=LlamafileConfig(**data.get('llamafile', {})),
        validation=ValidationConfig(**data.get('validation', {})),
    )

def save_config(config: Config, path: Path) -> None:
    """Save configuration to TOML file, preserving comments."""
    path.parent.mkdir(parents=True, exist_ok=True)

    # If file exists, load and preserve comments
    if path.exists():
        with open(path, 'r') as f:
            data = tomlkit.load(f)
    else:
        data = tomlkit.document()

    # Update values while preserving structure
    if 'ai' not in data:
        data['ai'] = tomlkit.table()
    data['ai']['model'] = config.ai.model
    data['ai']['temperature'] = config.ai.temperature
    data['ai']['max_tokens'] = config.ai.max_tokens

    if 'llamafile' not in data:
        data['llamafile'] = tomlkit.table()
    data['llamafile']['path'] = config.llamafile.path
    data['llamafile']['model_path'] = config.llamafile.model_path

    if 'validation' not in data:
        data['validation'] = tomlkit.table()
    data['validation']['auto_detect'] = config.validation.auto_detect
    data['validation']['max_retries'] = config.validation.max_retries

    if config.validation.validator_command:
        data['validation']['validator_command'] = config.validation.validator_command
    if config.validation.system_prompt:
        data['validation']['system_prompt'] = config.validation.system_prompt

    with open(path, 'w') as f:
        tomlkit.dump(data, f)

def get_config_path() -> Path:
    """Get the standard config path following XDG spec."""
    config_dir = Path.home() / '.config' / 'commit-polish'
    return config_dir / 'config.toml'

# Usage
if __name__ == '__main__':
    config_path = get_config_path()
    if config_path.exists():
        config = load_config(config_path)
        print(f"Model: {config.ai.model}")
    else:
        # Create new config
        config = Config(
            ai=AIConfig(),
            llamafile=LlamafileConfig(
                path='/home/user/.local/bin/llamafile',
                model_path='/home/user/.local/share/commit-polish/models/gemma-3-3b.gguf',
            ),
            validation=ValidationConfig(),
        )
        save_config(config, config_path)
        print("Config created at", config_path)
```

## TOML Syntax Reference

### Basic Types

```toml
# Strings
string = "Hello, World!"
multiline = """
Multiple
lines
"""

# Numbers
integer = 42
float = 3.14
scientific = 1e10

# Boolean
flag = true

# Date/Time
datetime = 2024-01-15T10:30:00Z
date = 2024-01-15
time = 10:30:00
```

### Tables (Sections)

```toml
# Standard table
[table]
key = "value"

# Nested table
[parent.child]
key = "value"

# Inline table
point = { x = 1, y = 2 }
```

### Arrays

```toml
# Basic array
numbers = [1, 2, 3]

# Array of tables
[[products]]
name = "Widget"
price = 9.99

[[products]]
name = "Gadget"
price = 19.99
```

## Type Conversions

| TOML Type | Python Type |
|-----------|-------------|
| String | `str` |
| Integer | `int` |
| Float | `float` |
| Boolean | `bool` |
| Offset Date-Time | `datetime.datetime` |
| Local Date-Time | `datetime.datetime` |
| Local Date | `datetime.date` |
| Local Time | `datetime.time` |
| Array | `list` |
| Table | `dict` |

## Package Dependencies

For `pyproject.toml`:

```toml
[project]
dependencies = [
    "tomlkit>=0.12.0",
]
```

Or for optional TOML support:

```toml
[project.optional-dependencies]
config = [
    "tomlkit>=0.12.0",
]
```

## Common Patterns in commit-polish

### Pattern 1: Initialize Config if Missing

```python
import tomlkit
from tomlkit.exceptions import ParseError
from pathlib import Path

def ensure_config_exists(config_path: Path) -> tomlkit.TOMLDocument:
    """Load config or create default if missing."""
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return tomlkit.load(f)
        except ParseError as e:
            raise ValueError(f"Invalid config at line {e.line}: {e}")

    # Create default config
    config = tomlkit.document()
    config.add(tomlkit.comment("Configuration for commit-polish"))
    config.add(tomlkit.nl())

    config.add('ai', tomlkit.table())
    config['ai']['model'] = 'llamafile/gemma-3-3b'
    config['ai']['temperature'] = 0.3
    config['ai']['max_tokens'] = 200

    config.add('llamafile', tomlkit.table())
    config['llamafile']['path'] = '/usr/local/bin/llamafile'

    config.add('validation', tomlkit.table())
    config['validation']['auto_detect'] = True
    config['validation']['max_retries'] = 3

    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        tomlkit.dump(config, f)

    return config
```

### Pattern 2: Update Single Key with Comment Preservation

```python
import tomlkit

def update_config_value(config_path: str, section: str, key: str, value) -> None:
    """Update a single value while preserving all comments."""
    with open(config_path, 'r') as f:
        config = tomlkit.load(f)

    if section not in config:
        config[section] = tomlkit.table()

    config[section][key] = value

    with open(config_path, 'w') as f:
        tomlkit.dump(config, f)

# Usage
update_config_value('config.toml', 'ai', 'temperature', 0.5)
```

### Pattern 3: Validate Config Structure

```python
import tomlkit
from tomlkit.exceptions import ParseError

def validate_config(config_path: str) -> tuple[bool, str]:
    """Validate config structure and return (is_valid, error_message)."""
    try:
        with open(config_path, 'r') as f:
            config = tomlkit.load(f)
    except FileNotFoundError:
        return False, "Config file not found"
    except ParseError as e:
        return False, f"Invalid TOML syntax at line {e.line}, column {e.col}"

    required_sections = ['ai', 'llamafile', 'validation']
    missing = [s for s in required_sections if s not in config]

    if missing:
        return False, f"Missing required sections: {', '.join(missing)}"

    # Validate specific keys
    if 'model' not in config.get('ai', {}):
        return False, "Missing required key: ai.model"

    return True, ""

# Usage
is_valid, error = validate_config('config.toml')
if not is_valid:
    print(f"Config validation failed: {error}")
```

### Pattern 4: Atomic Config Updates

```python
import tomlkit
from pathlib import Path
import tempfile
import shutil

def atomic_config_update(config_path: Path, updates: dict) -> None:
    """Update config atomically to prevent corruption on failure."""
    # Read existing config
    with open(config_path, 'r') as f:
        config = tomlkit.load(f)

    # Apply updates
    for section, values in updates.items():
        if section not in config:
            config[section] = tomlkit.table()
        for key, value in values.items():
            config[section][key] = value

    # Write to temp file first
    temp_fd, temp_path = tempfile.mkstemp(suffix='.toml')
    try:
        with open(temp_fd, 'w') as f:
            tomlkit.dump(config, f)
        # Atomic replace
        shutil.move(temp_path, config_path)
    except Exception:
        Path(temp_path).unlink(missing_ok=True)
        raise

# Usage
atomic_config_update(
    Path('config.toml'),
    {'ai': {'temperature': 0.7, 'max_tokens': 300}}
)
```

## Comparison: tomlkit vs tomllib + tomli_w

| Feature | tomlkit | tomllib + tomli_w |
|---------|---------|-------------------|
| Reading | Yes | Yes (tomllib) |
| Writing | Yes | Yes (tomli_w) |
| Comment preservation | Yes | No |
| Format preservation | Yes | No |
| Single library | Yes | No (2 libs) |
| Python version | >=3.8 | 3.11+ (tomllib) |
| TOML version | 1.0.0 | 1.0.0 |
| Use case | Config files with preservation | One-time read/write |

**For commit-polish**: tomlkit is the clear choice because:
- We need to preserve user comments in config files
- We may need to update config without losing formatting
- Single library simplifies dependency management
