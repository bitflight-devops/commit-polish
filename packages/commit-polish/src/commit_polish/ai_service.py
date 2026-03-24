"""LiteLLM wrapper with llamafile routing for commit-polish."""

from __future__ import annotations

import re

import litellm

from commit_polish.config import Config

# Suppress LiteLLM's verbose output
litellm.suppress_debug_info = True

# EOS tokens that small models sometimes leak into their output
_EOS_TOKENS = ("</s>", "<|im_end|>", "<|endoftext|>", "<|eot_id|>", "<|end|>")

# Matches a properly formatted conventional commit first line
_CONVENTIONAL_RE = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(\([^)]+\))?!?:\s+\S",
    re.MULTILINE,
)

# Matches the labeled field format some small models emit instead of real syntax
_TYPE_RE = re.compile(r"^Type:\s*(\w+)", re.IGNORECASE | re.MULTILINE)
_SCOPE_RE = re.compile(r"^Scope:\s*(\S[^\n]*)", re.IGNORECASE | re.MULTILINE)
_DESC_RE = re.compile(
    r"^(?:Short\s+)?Description:\s*(\S[^\n]*)", re.IGNORECASE | re.MULTILINE
)


def _clean_response(text: str) -> str:
    """Strip EOS tokens and normalise model output to conventional commit format.

    Small models often leak EOS tokens or emit a labeled field format
    (Type:/Scope:/Description:) instead of conventional commit syntax.
    This function normalises both cases into a clean commit message.
    """
    for token in _EOS_TOKENS:
        text = text.replace(token, "")
    text = text.strip()

    # Already in conventional commit format — return from that line onward.
    m = _CONVENTIONAL_RE.search(text)
    if m:
        return text[m.start() :].strip()

    # Reconstruct from labeled fields if present.
    type_m = _TYPE_RE.search(text)
    desc_m = _DESC_RE.search(text)
    if type_m and desc_m:
        commit_type = type_m.group(1).lower()
        scope_m = _SCOPE_RE.search(text)
        scope = f"({scope_m.group(1).strip()})" if scope_m else ""
        desc = desc_m.group(1).strip().rstrip(".")
        return f"{commit_type}{scope}: {desc}"

    return text


class AIServiceError(Exception):
    """Raised when the AI service is unavailable or returns an error."""


async def generate_commit_message(
    diff: str,
    original_message: str,
    system_prompt: str,
    config: Config,
    extra_context: str = "",
) -> str:
    """Generate a polished commit message from a diff and original message.

    Args:
        diff: The staged git diff.
        original_message: The original commit message (may be empty or a rough draft).
        system_prompt: The system prompt describing the desired format.
        config: The loaded commit-polish configuration.
        extra_context: Optional additional context (e.g., validation errors).

    Returns:
        The generated commit message string.

    Raises:
        AIServiceError: If the LLM call fails.
    """
    user_parts = []

    if diff:
        # Truncate large diffs — small models have limited context windows.
        # 4 000 chars ≈ 1 000 tokens, leaving room for system prompt + output.
        max_diff_chars = 4000
        truncated = diff[:max_diff_chars]
        suffix = f"\n… (truncated, {len(diff) - max_diff_chars} chars omitted)" if len(diff) > max_diff_chars else ""
        user_parts.append(f"Git diff (staged changes):\n```\n{truncated}{suffix}\n```")

    if original_message.strip():
        user_parts.append(f"Original commit message: {original_message.strip()}")

    if extra_context:
        user_parts.append(extra_context)

    user_parts.append(
        "Please write a polished commit message following the instructions above."
    )

    user_content = "\n\n".join(user_parts)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    api_base: str | None = None
    if config.ai.model.startswith("llamafile/"):
        api_base = config.ai.api_base

    try:
        response = await litellm.acompletion(
            model=config.ai.model,
            messages=messages,
            temperature=config.ai.temperature,
            max_tokens=config.ai.max_tokens,
            api_base=api_base,
        )
    except litellm.APIConnectionError as e:
        raise AIServiceError(
            f"Cannot connect to LLM at {api_base or 'default endpoint'}. "
            "Is the llamafile server running? "
            f"Start it with: ./llamafile --server -m model.gguf --nobrowser --port 8080\n"
            f"Details: {e}"
        ) from e
    except Exception as e:
        raise AIServiceError(f"LLM call failed: {e}") from e

    content = response.choices[0].message.content
    if not content:
        raise AIServiceError("LLM returned an empty response.")

    return _clean_response(str(content))
