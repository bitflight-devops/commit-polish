# Conventional Commits Reference Documentation

## Overview

Conventional Commits is a specification for adding human and machine-readable meaning to commit messages. It provides a lightweight convention for creating an explicit commit history, enabling automated changelog generation and semantic versioning.

**Key Feature for commit-polish**: This is the primary commit message format the tool generates.

## Official Documentation

### Primary Sources

- [Conventional Commits v1.0.0 Specification](https://www.conventionalcommits.org/en/v1.0.0/) - The official specification
- [GitHub Repository](https://github.com/conventional-commits/conventionalcommits.org) - Source repository for the specification
- [Specification Source (Markdown)](https://github.com/conventional-commits/conventionalcommits.org/blob/master/content/v1.0.0/index.md) - Raw specification content

### Related Standards and Tools

- [Angular Commit Message Guidelines](https://github.com/angular/angular/blob/main/contributing-docs/commit-message-guidelines.md) - The convention that inspired Conventional Commits
- [@commitlint/config-conventional](https://github.com/conventional-changelog/commitlint/tree/master/%40commitlint/config-conventional) - Commitlint shareable config
- [@commitlint/config-angular](https://github.com/conventional-changelog/commitlint/tree/master/%40commitlint/config-angular) - Angular-style commitlint config
- [Semantic Versioning (SemVer)](https://semver.org/) - Versioning standard that Conventional Commits dovetails with
- [Git Trailer Format](https://git-scm.com/docs/git-interpret-trailers) - Convention that inspired footer format

### Specification References

- [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt) - Key words used in the specification (MUST, SHALL, etc.)
- [Creative Commons CC BY 3.0](https://creativecommons.org/licenses/by/3.0/) - License for the specification

## Message Structure

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Components

| Component | Required | Description |
|-----------|----------|-------------|
| type | Yes | Commit category (feat, fix, etc.) |
| scope | No | Section of codebase affected |
| description | Yes | Short summary of changes |
| body | No | Detailed explanation |
| footer | No | Breaking changes, issue refs |

## Commit Types

### Required Types (SemVer Impact)

These types are defined by the Conventional Commits specification and directly affect semantic versioning:

| Type | Description | SemVer | Example |
|------|-------------|--------|---------|
| `feat` | A new feature for the user | MINOR (0.X.0) | `feat: add user authentication` |
| `fix` | A bug fix for the user | PATCH (0.0.X) | `fix: prevent crash on empty input` |

### Recommended Types (Angular Convention)

These types are recommended by [@commitlint/config-conventional](https://github.com/conventional-changelog/commitlint/tree/master/%40commitlint/config-conventional), based on the [Angular convention](https://github.com/angular/angular/blob/main/contributing-docs/commit-message-guidelines.md). They have no implicit SemVer effect unless they include a BREAKING CHANGE.

| Type | Description | Example |
|------|-------------|---------|
| `build` | Changes to build system or external dependencies (gulp, broccoli, npm) | `build: update webpack to v5` |
| `ci` | Changes to CI configuration files and scripts (GitHub Actions, CircleCI) | `ci: add Node 18 to test matrix` |
| `docs` | Documentation only changes | `docs: update API reference` |
| `perf` | A code change that improves performance | `perf: reduce bundle size by 20%` |
| `refactor` | A code change that neither fixes a bug nor adds a feature | `refactor: extract validation logic` |
| `style` | Changes that do not affect code meaning (whitespace, formatting, semicolons) | `style: fix indentation` |
| `test` | Adding missing tests or correcting existing tests | `test: add unit tests for parser` |

### Additional Common Types

These types are commonly used but not part of the Angular convention:

| Type | Description | Example |
|------|-------------|---------|
| `chore` | Other changes that don't modify src or test files | `chore: update .gitignore` |
| `revert` | Reverts a previous commit | `revert: feat: add user auth` |

**Note**: The Conventional Commits specification does not mandate specific types beyond `feat` and `fix`. Teams can define their own types, but the Angular convention types are widely adopted and supported by most tooling.

## Specification Rules (Complete)

The following 16 rules constitute the official Conventional Commits 1.0.0 specification. The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" are interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

### Rules 1-5: Type and Scope

1. Commits **MUST** be prefixed with a type, which consists of a noun, `feat`, `fix`, etc., followed by the OPTIONAL scope, OPTIONAL `!`, and REQUIRED terminal colon and space.

2. The type `feat` **MUST** be used when a commit adds a new feature to your application or library.

3. The type `fix` **MUST** be used when a commit represents a bug fix for your application.

4. A scope **MAY** be provided after a type. A scope **MUST** consist of a noun describing a section of the codebase surrounded by parenthesis, e.g., `fix(parser):`

5. A description **MUST** immediately follow the colon and space after the type/scope prefix. The description is a short summary of the code changes, e.g., *fix: array parsing issue when multiple spaces were contained in string*.

### Rules 6-7: Body

6. A longer commit body **MAY** be provided after the short description, providing additional contextual information about the code changes. The body **MUST** begin one blank line after the description.

7. A commit body is free-form and **MAY** consist of any number of newline separated paragraphs.

### Rules 8-10: Footer

8. One or more footers **MAY** be provided one blank line after the body. Each footer **MUST** consist of a word token, followed by either a `:<space>` or `<space>#` separator, followed by a string value (inspired by the [git trailer convention](https://git-scm.com/docs/git-interpret-trailers)).

9. A footer's token **MUST** use `-` in place of whitespace characters, e.g., `Acked-by` (this helps differentiate the footer section from a multi-paragraph body). An exception is made for `BREAKING CHANGE`, which **MAY** also be used as a token.

10. A footer's value **MAY** contain spaces and newlines, and parsing **MUST** terminate when the next valid footer token/separator pair is observed.

### Rules 11-13: Breaking Changes

11. Breaking changes **MUST** be indicated in the type/scope prefix of a commit, or as an entry in the footer.

12. If included as a footer, a breaking change **MUST** consist of the uppercase text BREAKING CHANGE, followed by a colon, space, and description, e.g., *BREAKING CHANGE: environment variables now take precedence over config files*.

13. If included in the type/scope prefix, breaking changes **MUST** be indicated by a `!` immediately before the `:`. If `!` is used, `BREAKING CHANGE:` **MAY** be omitted from the footer section, and the commit description **SHALL** be used to describe the breaking change.

### Rules 14-16: Additional Rules

14. Types other than `feat` and `fix` **MAY** be used in your commit messages, e.g., *docs: update ref docs.*

15. The units of information that make up Conventional Commits **MUST NOT** be treated as case sensitive by implementors, with the exception of BREAKING CHANGE which **MUST** be uppercase.

16. BREAKING-CHANGE **MUST** be synonymous with BREAKING CHANGE, when used as a token in a footer.

### Quick Reference Examples

```
feat(parser): add ability to parse arrays
fix(auth): handle token expiration
docs: correct spelling in README
```

### Footer Examples

```
Reviewed-by: Alice <alice@example.com>
Refs: #123
Co-authored-by: Bob <bob@example.com>
Fixes #456
```

## Breaking Changes

### Methods to Indicate Breaking Changes

1. **Footer**: `BREAKING CHANGE: description`
2. **Type suffix**: `feat!: description`
3. **Type+scope suffix**: `feat(api)!: description`

### Footer Format

```
feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files
```

### Exclamation Mark Format

```
feat!: remove support for Node 6

feat(api)!: send an email to the customer when a product is shipped
```

### Rules

- `BREAKING CHANGE` MUST be uppercase
- `BREAKING-CHANGE` is synonymous when used as footer token
- Breaking changes MUST correlate to MAJOR version bump

## Examples (Copy-Paste Ready)

The following examples are taken directly from the official Conventional Commits specification.

### Simple Commits (No Body)

```
feat: add user authentication
```

```
fix: prevent crash on empty input
```

```
docs: correct spelling of CHANGELOG
```

### Commit with Scope

```
feat(lang): add Polish language
```

```
feat(parser): add ability to parse arrays
```

```
fix(auth): handle token expiration correctly
```

### Breaking Change with Footer

```
feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files
```

### Breaking Change with `!` (No Footer)

```
feat!: send an email to the customer when a product is shipped
```

### Breaking Change with Scope and `!`

```
feat(api)!: send an email to the customer when a product is shipped
```

### Breaking Change with Both `!` and Footer

```
chore!: drop support for Node 6

BREAKING CHANGE: use JavaScript features not available in Node 6.
```

### Commit with Multi-Paragraph Body and Multiple Footers

```
fix: prevent racing of requests

Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request.

Remove timeouts which were used to mitigate the racing issue but are
obsolete now.

Reviewed-by: Z
Refs: #123
```

### Revert Commit

```
revert: let us never again speak of the noodle incident

Refs: 676104e, a215868
```

### Performance Improvement

```
perf: reduce memory allocation in parser by 40%

Replace string concatenation with StringBuilder pattern.
Benchmark results show 40% reduction in heap allocations.

Refs: #456
```

### Refactoring

```
refactor: extract authentication logic into separate module

Move auth-related functions from utils.py to auth.py.
No functional changes.
```

### CI/Build Changes

```
ci: add Node 18 to test matrix
```

```
build: upgrade webpack from v4 to v5

- Update webpack.config.js for v5 compatibility
- Replace deprecated plugins
- Update all loader dependencies

Refs: #789
```

### Test Changes

```
test: add unit tests for user validation

Cover edge cases for email validation and password strength.
```

### Style Changes

```
style: format code according to prettier config
```

### Chore/Maintenance

```
chore: update .gitignore to exclude IDE files
```

## Description Best Practices

Based on the [Angular Commit Message Guidelines](https://github.com/angular/angular/blob/main/contributing-docs/commit-message-guidelines.md):

### Summary/Description Guidelines

- Use the **imperative, present tense**: "change" not "changed" nor "changes"
- **Do not capitalize** the first letter
- **No period** (.) at the end
- Keep the entire header (type + scope + description) **under 72 characters**

### Good Examples

```
feat: add validation for email input
fix: handle null pointer in user service
docs: update installation instructions
refactor: simplify authentication flow
```

### Bad Examples (Avoid These)

```
feat: Added validation for email input     # Past tense
fix: Handles null pointer in user service  # Third person
docs: Update installation instructions.    # Period at end, capitalized
FEAT: add validation                       # Uppercase type (technically allowed but inconsistent)
```

### Body Guidelines

- Use imperative, present tense (same as summary)
- Explain the **motivation** for the change
- Include comparison of previous vs new behavior when helpful
- Body **MUST** begin with one blank line after the description
- Recommended minimum: 20 characters when body is present

## Semantic Versioning Correlation

| Commit Type | Version Bump |
|-------------|--------------|
| `fix` | PATCH (0.0.X) |
| `feat` | MINOR (0.X.0) |
| `BREAKING CHANGE` | MAJOR (X.0.0) |

### Version Bump Priority

When determining the version bump for a release:

1. If **any** commit contains `BREAKING CHANGE` (footer or `!`): **MAJOR**
2. Else if **any** commit is `feat`: **MINOR**
3. Else if **any** commit is `fix`: **PATCH**
4. Else: No version change

## Default System Prompt for commit-polish

```
Write a commit message in the Conventional Commits format. Use the structure:
<type>(<optional scope>): <short description>

<optional body>

<optional footer>

Allowed types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert

Guidelines:
- Description should be lowercase, imperative mood, no period at end
- Keep first line under 72 characters
- Use body for additional context with bullet points if needed
- Use BREAKING CHANGE: in footer for breaking changes
- Reference issues in footer (e.g., Refs: #123)

Just return the commit message, do not include any other text.
```

## Validation Regex

### Header Validation

```regex
^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?!?:\s.+$
```

### Python Validation

```python
import re

CONVENTIONAL_COMMIT_PATTERN = re.compile(
    r'^(?P<type>feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)'
    r'(?:\((?P<scope>[^)]+)\))?'
    r'(?P<breaking>!)?'
    r':\s'
    r'(?P<description>.+)$'
)

def validate_header(header: str) -> bool:
    """Validate commit header follows Conventional Commits."""
    return bool(CONVENTIONAL_COMMIT_PATTERN.match(header))

def parse_header(header: str) -> dict | None:
    """Parse commit header into components."""
    match = CONVENTIONAL_COMMIT_PATTERN.match(header)
    if not match:
        return None
    return {
        'type': match.group('type'),
        'scope': match.group('scope'),
        'breaking': bool(match.group('breaking')),
        'description': match.group('description'),
    }
```

## Integration with Other Tools

### semantic-release

Uses Conventional Commits for automatic versioning:

```javascript
// release.config.js
module.exports = {
  branches: ['main'],
  plugins: [
    '@semantic-release/commit-analyzer',
    '@semantic-release/release-notes-generator',
  ],
};
```

### commitizen

Interactive commit message builder:

```json
// .cz.json
{
  "path": "cz-conventional-changelog"
}
```

### git-cliff

Changelog generator:

```toml
# cliff.toml
[git]
conventional_commits = true
```

## Why Use Conventional Commits

From the [official specification](https://www.conventionalcommits.org/en/v1.0.0/):

1. **Automatically generating CHANGELOGs** - Tools can parse commit history and generate release notes
2. **Automatically determining semantic version bumps** - Based on the types of commits landed
3. **Communicating the nature of changes** - To teammates, the public, and other stakeholders
4. **Triggering build and publish processes** - CI/CD pipelines can react to specific commit types
5. **Making it easier for people to contribute** - By allowing them to explore a more structured commit history

## FAQ

### Can I use custom types?

Yes, additional types are not mandated by the spec but have no implicit SemVer effect unless they include BREAKING CHANGE. Teams commonly add types like `chore`, `wip`, `deps`, etc.

### Is the spec case-sensitive?

Implementation-defined. Most tools normalize to lowercase. The only exception is `BREAKING CHANGE` which MUST be uppercase. Best practice: be consistent within your project.

### What about merge commits?

Merge commits are typically ignored by changelog generators. They don't need to follow the format.

### What if I accidentally use the wrong type?

- **Before merging/releasing**: Use `git rebase -i` to edit the commit history
- **After release**: The cleanup will depend on your tools and processes
- **Worst case**: A non-conforming commit will simply be missed by tools based on the spec

### Do all contributors need to use Conventional Commits?

No. If you use a squash-based workflow, lead maintainers can clean up commit messages when merging. Many teams configure their git system to automatically squash commits from a pull request and present a form for entering the proper commit message.

### How does Conventional Commits handle revert commits?

The specification does not define explicit revert behavior. The recommended approach is to use the `revert` type with a footer referencing the reverted commit SHAs:

```
revert: let us never again speak of the noodle incident

Refs: 676104e, a215868
```

### What if validation fails?

Tools like commitlint will reject the commit. commit-polish uses a retry loop with error feedback to the LLM to automatically correct the message format.
