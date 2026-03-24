"""Entry point for the prepare-commit-msg git hook.

Called by pre-commit with:
    commit-polish hook <commit_msg_file> [commit_source] [commit_sha]
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from commit_polish.config import load_config
from commit_polish.message_rewriter import rewrite_message_sync
from commit_polish.validators.detector import detect_validators


def get_staged_diff() -> str:
    """Get the staged diff (what will actually be committed)."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def run_hook(commit_msg_file: str) -> int:
    """Main hook entry point. Returns exit code."""
    msg_path = Path(commit_msg_file)

    if not msg_path.exists():
        print(f"commit-polish: message file not found: {commit_msg_file}", file=sys.stderr)
        return 1

    original_message = msg_path.read_text().strip()

    # Skip merge commits, fixup commits, etc.
    if original_message.startswith("Merge ") or original_message.startswith("fixup! "):
        return 0

    # Skip if the message is already detailed (user wrote it intentionally)
    lines = [l for l in original_message.splitlines() if not l.startswith("#")]
    meaningful = "\n".join(lines).strip()
    if len(meaningful) > 72 and "\n" in meaningful:
        return 0  # Looks intentional — don't overwrite

    config = load_config()
    diff = get_staged_diff()

    validators = detect_validators(
        validator_command=config.validation.validator_command,
        auto_detect=config.validation.auto_detect,
    )

    try:
        result = rewrite_message_sync(
            diff=diff,
            original_message=meaningful,
            config=config,
            validators=validators,
        )
    except Exception as e:
        print(f"commit-polish: LLM unavailable, keeping original message. ({e})", file=sys.stderr)
        return 0  # Don't block the commit

    # Write the polished message back
    msg_path.write_text(result.message + "\n")
    return 0


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: commit-polish hook <commit_msg_file>", file=sys.stderr)
        sys.exit(1)
    sys.exit(run_hook(sys.argv[1]))
