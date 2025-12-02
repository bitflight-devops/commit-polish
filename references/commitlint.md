# Commitlint Reference Documentation

## Overview

Commitlint is a tool that checks if commit messages meet the Conventional Commits format. It supports shareable configurations, custom rules, and integration with pre-commit hooks.

**Key Feature for commit-polish**: Auto-detection of commitlint configuration to extract rules for LLM prompts.

## Official Documentation

- [Commitlint Official Site](https://commitlint.js.org/)
- [Configuration Reference](https://commitlint.js.org/reference/configuration.html)
- [Rules Reference](https://commitlint.js.org/reference/rules.html)
- [CLI Reference](https://commitlint.js.org/reference/cli.html)
- [Getting Started Guide](https://commitlint.js.org/guides/getting-started.html)
- [GitHub Repository](https://github.com/conventional-changelog/commitlint)

## Configuration File Detection

Commitlint uses [cosmiconfig](https://github.com/cosmiconfig/cosmiconfig) to find configuration. It searches for these files in order:

### Dedicated Config Files

```
.commitlintrc
.commitlintrc.json
.commitlintrc.yaml
.commitlintrc.yml
.commitlintrc.js
.commitlintrc.cjs
.commitlintrc.mjs
.commitlintrc.ts
.commitlintrc.cts
commitlint.config.js
commitlint.config.cjs
commitlint.config.mjs
commitlint.config.ts
commitlint.config.cts
```

### Package Files

```json
// package.json
{
  "commitlint": {
    "extends": ["@commitlint/config-conventional"]
  }
}
```

```yaml
# package.yaml (PNPM)
commitlint:
  extends:
    - "@commitlint/config-conventional"
```

## Configuration Formats

### JavaScript (ES Modules) - Recommended

```javascript
// commitlint.config.js or commitlint.config.mjs
export default {
  extends: ['@commitlint/config-conventional'],
};
```

### JavaScript (CommonJS)

```javascript
// commitlint.config.cjs
module.exports = {
  extends: ['@commitlint/config-conventional'],
};
```

### TypeScript

```typescript
// commitlint.config.ts
import type { UserConfig } from '@commitlint/types';
import { RuleConfigSeverity } from '@commitlint/types';

const config: UserConfig = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [RuleConfigSeverity.Error, 'always', ['feat', 'fix', 'docs']],
  },
};

export default config;
```

### JSON

```json
// .commitlintrc.json
{
  "extends": ["@commitlint/config-conventional"]
}
```

### YAML

```yaml
# .commitlintrc.yml
extends:
  - "@commitlint/config-conventional"
```

## Complete Configuration Object Schema

```javascript
// commitlint.config.js
export default {
  // Extend shareable configs (resolved via node resolution)
  extends: ['@commitlint/config-conventional'],

  // Parser preset for parsing commit messages
  parserPreset: 'conventional-changelog-atom',

  // Output formatter
  formatter: '@commitlint/format',

  // Custom rules (override inherited rules)
  rules: {
    'type-enum': [2, 'always', ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore']],
  },

  // Functions that return true to ignore specific commits
  // Merged with default ignores (merge commits, reverts, semver tags)
  ignores: [(commit) => commit.includes('WIP')],

  // Whether to use default ignore patterns
  // Default patterns: 'Merge pull request', 'Revert X', 'v1.2.3', etc.
  defaultIgnores: true,

  // Custom help URL shown on failure
  helpUrl: 'https://example.com/commit-guidelines',

  // Prompt configuration (for @commitlint/cz-commitlint)
  prompt: {
    messages: {},
    questions: {
      type: {
        description: 'Select the type of change:',
      },
    },
  },
};
```

## Rule Configuration Format

Rules are configured as arrays: `[level, applicability, value]`

### Severity Levels

| Level | Meaning | TypeScript Enum |
|-------|---------|-----------------|
| 0 | Disabled | `RuleConfigSeverity.Disabled` |
| 1 | Warning | `RuleConfigSeverity.Warning` |
| 2 | Error | `RuleConfigSeverity.Error` |

### Applicability

| Applicability | Meaning |
|---------------|---------|
| `'always'` | Rule must match |
| `'never'` | Rule must not match |

### Example Rules

```javascript
rules: {
  // Error if type is not in enum
  'type-enum': [2, 'always', ['feat', 'fix', 'docs', 'style', 'refactor', 'perf', 'test', 'build', 'ci', 'chore', 'revert']],

  // Error if type is empty
  'type-empty': [2, 'never'],

  // Error if subject is empty
  'subject-empty': [2, 'never'],

  // Error if header exceeds 100 chars
  'header-max-length': [2, 'always', 100],

  // Error if subject ends with period
  'subject-full-stop': [2, 'never', '.'],

  // Warning if body doesn't have leading blank line
  'body-leading-blank': [1, 'always'],
}
```

## Complete Rules Reference

### Type Rules

| Rule | Condition | Default Applicability |
|------|-----------|----------------------|
| `type-enum` | `type` is found in value | `always` |
| `type-case` | `type` is in case `value` | `always`, `'lower-case'` |
| `type-empty` | `type` is empty | `never` |
| `type-max-length` | `type` has `value` or less characters | `always`, `Infinity` |
| `type-min-length` | `type` has `value` or more characters | `always`, `0` |

### Subject Rules

| Rule | Condition | Default Applicability |
|------|-----------|----------------------|
| `subject-case` | `subject` is in case `value` | `always` |
| `subject-empty` | `subject` is empty | `never` |
| `subject-full-stop` | `subject` ends with `value` | `never`, `'.'` |
| `subject-max-length` | `subject` has `value` or less characters | `always`, `Infinity` |
| `subject-min-length` | `subject` has `value` or more characters | `always`, `0` |
| `subject-exclamation-mark` | `subject` has exclamation before `:` | `never` |

### Scope Rules

| Rule | Condition | Default Applicability |
|------|-----------|----------------------|
| `scope-enum` | `scope` is found in value | `always`, `[]` |
| `scope-case` | `scope` is in case `value` | `always`, `'lower-case'` |
| `scope-empty` | `scope` is empty | `never` |
| `scope-max-length` | `scope` has `value` or less characters | `always`, `Infinity` |
| `scope-min-length` | `scope` has `value` or more characters | `always`, `0` |

### Header Rules

| Rule | Condition | Default Applicability |
|------|-----------|----------------------|
| `header-case` | `header` is in case `value` | `always`, `'lower-case'` |
| `header-full-stop` | `header` ends with `value` | `never`, `'.'` |
| `header-max-length` | `header` has `value` or less characters | `always`, `72` |
| `header-min-length` | `header` has `value` or more characters | `always`, `0` |
| `header-trim` | `header` has no leading/trailing whitespace | `always` |

### Body Rules

| Rule | Condition | Default Applicability |
|------|-----------|----------------------|
| `body-leading-blank` | `body` begins with blank line | `always` |
| `body-empty` | `body` is empty | `never` |
| `body-max-length` | `body` has `value` or less characters | `always`, `Infinity` |
| `body-max-line-length` | `body` lines have `value` or less characters (URLs excluded) | `always`, `Infinity` |
| `body-min-length` | `body` has `value` or more characters | `always`, `0` |
| `body-case` | `body` is in case `value` | `always`, `'lower-case'` |
| `body-full-stop` | `body` ends with `value` | `never`, `'.'` |

### Footer Rules

| Rule | Condition | Default Applicability |
|------|-----------|----------------------|
| `footer-leading-blank` | `footer` begins with blank line | `always` |
| `footer-empty` | `footer` is empty | `never` |
| `footer-max-length` | `footer` has `value` or less characters | `always`, `Infinity` |
| `footer-max-line-length` | `footer` lines have `value` or less characters | `always`, `Infinity` |
| `footer-min-length` | `footer` has `value` or more characters | `always`, `0` |

### Special Rules

| Rule | Condition |
|------|-----------|
| `signed-off-by` | `message` contains `value` (e.g., `'Signed-off-by:'`) |
| `trailer-exists` | `message` has trailer `value` |
| `references-empty` | `references` has at least one entry |
| `breaking-change-exclamation-mark` | XNOR: both or neither `!` in header and `BREAKING CHANGE` in footer |

### Case Values

For rules that check case (`*-case`), valid values are:

```javascript
[
  'lower-case',    // lowercase
  'upper-case',    // UPPERCASE
  'camel-case',    // camelCase
  'kebab-case',    // kebab-case
  'pascal-case',   // PascalCase
  'sentence-case', // Sentence case
  'snake-case',    // snake_case
  'start-case',    // Start Case
]
```

## @commitlint/config-conventional Rules

The most common shareable configuration. Default rules with level `error`:

| Rule | Configuration | Example Pass | Example Fail |
|------|---------------|--------------|--------------|
| `type-enum` | `['build', 'chore', 'ci', 'docs', 'feat', 'fix', 'perf', 'refactor', 'revert', 'style', 'test']` | `fix: message` | `foo: message` |
| `type-case` | `'lowerCase'` | `fix: message` | `FIX: message` |
| `type-empty` | `never` | `fix: message` | `: message` |
| `subject-case` | `never` + `['sentence-case', 'start-case', 'pascal-case', 'upper-case']` | `fix: some message` | `fix: Some Message` |
| `subject-empty` | `never` | `fix: message` | `fix:` |
| `subject-full-stop` | `never`, `'.'` | `fix: message` | `fix: message.` |
| `header-max-length` | `100` | Short header | Header > 100 chars |
| `body-leading-blank` | `always` (warning) | Blank line before body | No blank line |
| `body-max-line-length` | `100` | Lines <= 100 chars | Line > 100 chars |
| `footer-leading-blank` | `always` (warning) | Blank line before footer | No blank line |
| `footer-max-line-length` | `100` | Lines <= 100 chars | Line > 100 chars |

## CLI Usage

### Installation

```bash
# npm
npm install -D @commitlint/cli @commitlint/config-conventional

# yarn
yarn add -D @commitlint/cli @commitlint/config-conventional

# pnpm
pnpm add -D @commitlint/cli @commitlint/config-conventional
```

### CLI Reference

```
@commitlint/cli - Lint your commit messages

[input] reads from stdin if --edit, --env, --from and --to are omitted

Options:
  -c, --color          toggle colored output           [boolean] [default: true]
  -g, --config         path to the config file                          [string]
  -d, --cwd            directory to execute in                          [string]
  -e, --edit           read last commit message from file               [string]
  -E, --env            check message from environment variable          [string]
  -x, --extends        array of shareable configurations to extend       [array]
  -H, --help-url       help url in error message                        [string]
  -f, --from           lower end of commit range to lint                [string]
      --from-last-tag  use last tag as lower end of range              [boolean]
      --git-log-args   additional git log arguments                     [string]
  -l, --last           just analyze the last commit                    [boolean]
  -o, --format         output format of results                         [string]
  -p, --parser-preset  parser preset for conventional-commits-parser    [string]
  -q, --quiet          toggle console output          [boolean] [default: false]
  -t, --to             upper end of commit range to lint                [string]
  -V, --verbose        enable verbose output                           [boolean]
  -s, --strict         strict mode; exit 2 for warnings, 3 for errors  [boolean]
  -v, --version        display version information                     [boolean]
  -h, --help           Show help                                       [boolean]
```

### Common CLI Commands

```bash
# Lint the last commit
npx commitlint --last

# Lint a range of commits
npx commitlint --from HEAD~5

# Lint from a specific commit
npx commitlint --from abc1234

# Lint message from stdin
echo "feat: add feature" | npx commitlint

# Lint message from file
npx commitlint < .git/COMMIT_EDITMSG

# Lint with edit flag (reads .git/COMMIT_EDITMSG)
npx commitlint --edit

# Lint with custom config path
npx commitlint --config ./custom-commitlint.config.js

# Print resolved config
npx commitlint --print-config

# Strict mode (warnings become exit code 2)
npx commitlint --last --strict
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (no errors) |
| 1 | Lint errors found |
| 2 | Warnings found (strict mode only) |
| 3 | Errors found (strict mode) |
| 9 | Config file missing (with -g flag) |

## Programmatic API

### Loading Configuration

```javascript
import load from '@commitlint/load';

async function getCommitlintConfig() {
  const config = await load();
  console.log(config.rules);
  return config;
}
```

### Linting a Message

```javascript
import load from '@commitlint/load';
import lint from '@commitlint/lint';

async function validateMessage(message) {
  const config = await load();
  const result = await lint(message, config.rules);

  return {
    valid: result.valid,
    errors: result.errors,
    warnings: result.warnings,
  };
}
```

## Detection Pattern for commit-polish

```python
from pathlib import Path
import json

COMMITLINT_CONFIG_FILES = [
    '.commitlintrc',
    '.commitlintrc.json',
    '.commitlintrc.yaml',
    '.commitlintrc.yml',
    '.commitlintrc.js',
    '.commitlintrc.cjs',
    '.commitlintrc.mjs',
    '.commitlintrc.ts',
    '.commitlintrc.cts',
    'commitlint.config.js',
    'commitlint.config.cjs',
    'commitlint.config.mjs',
    'commitlint.config.ts',
    'commitlint.config.cts',
]


def find_commitlint_config(repo_path: Path) -> Path | None:
    """Find commitlint configuration file in repository."""
    for config_file in COMMITLINT_CONFIG_FILES:
        config_path = repo_path / config_file
        if config_path.exists():
            return config_path

    # Check package.json for commitlint field
    package_json = repo_path / 'package.json'
    if package_json.exists():
        data = json.loads(package_json.read_text())
        if 'commitlint' in data:
            return package_json

    return None
```

## Validation Loop for commit-polish

```python
import subprocess


async def validate_with_commitlint(message: str, cwd: Path | None = None) -> tuple[bool, list[str]]:
    """
    Validate commit message with commitlint.

    Args:
        message: The commit message to validate
        cwd: Working directory (defaults to current directory)

    Returns:
        Tuple of (is_valid, error_messages)
    """
    result = subprocess.run(
        ['npx', 'commitlint'],
        input=message,
        capture_output=True,
        text=True,
        cwd=cwd,
    )

    if result.returncode == 0:
        return True, []

    # Parse errors from stderr
    errors = [line.strip() for line in result.stderr.split('\n') if line.strip()]
    return False, errors
```

### Validation Loop Pattern

1. LLM generates commit message based on diff and rules
2. Run commitlint on generated message
3. If validation fails, feed errors back to LLM with context
4. Retry (max 3 times by default)
5. Return final message (valid or best effort after retries)

## Common Pitfalls

1. **Node v24 ESM issues**: Use `.mjs` extension for ES modules config, or add `"type": "module"` to package.json
2. **Missing extends**: Config without `extends` or `rules` will fail with "Please add rules" error
3. **Case sensitivity**: Rule names are case-sensitive (`type-enum` not `Type-Enum`)
4. **Empty config error**: Config file must have at least `extends` or `rules` defined
5. **Scope enum empty array**: `scope-enum` with `[]` passes all scopes; use specific array to restrict
6. **Subject case trap**: `@commitlint/config-conventional` uses `never` with specific cases, meaning those cases are forbidden (not required)

## Extracting Rules for LLM Prompts

When generating prompts for LLMs based on commitlint config:

```python
def extract_rules_for_prompt(config: dict) -> str:
    """Extract commitlint rules into LLM-friendly format."""
    rules = config.get('rules', {})
    prompt_parts = []

    # Extract type-enum if present
    if 'type-enum' in rules:
        level, applicability, types = rules['type-enum']
        if level > 0 and applicability == 'always':
            prompt_parts.append(f"Allowed commit types: {', '.join(types)}")

    # Extract scope-enum if present
    if 'scope-enum' in rules:
        level, applicability, scopes = rules['scope-enum']
        if level > 0 and applicability == 'always' and scopes:
            prompt_parts.append(f"Allowed scopes: {', '.join(scopes)}")

    # Extract header-max-length
    if 'header-max-length' in rules:
        level, applicability, length = rules['header-max-length']
        if level > 0:
            prompt_parts.append(f"Header must be {length} characters or less")

    # Extract subject-case
    if 'subject-case' in rules:
        level, applicability, cases = rules['subject-case']
        if level > 0 and applicability == 'never':
            prompt_parts.append(f"Subject must NOT use: {', '.join(cases)}")

    return '\n'.join(prompt_parts)
```
