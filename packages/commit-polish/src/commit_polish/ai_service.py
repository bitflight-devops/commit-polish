"""LiteLLM wrapper with llamafile routing for commit-polish."""

from __future__ import annotations

import litellm

from commit_polish.config import Config

# Suppress LiteLLM's verbose output
litellm.suppress_debug_info = True


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
        user_parts.append(f"Git diff (staged changes):\n```\n{diff}\n```")

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

    return str(content).strip()
