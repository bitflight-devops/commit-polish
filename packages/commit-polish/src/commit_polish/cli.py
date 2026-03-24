"""CLI for commit-polish.

Commands:
  hook <file>           Run as a prepare-commit-msg hook (called by pre-commit)
  preview               Preview what the hook would generate for your staged changes
  test --message --diff Test with explicit inputs (no git repo needed)
  config init           Write a default config file
  config show           Show the current config
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table
from rich import box

from commit_polish.config import load_config, write_default_config, DEFAULT_CONFIG_PATH
from commit_polish.message_rewriter import rewrite_message_sync
from commit_polish.validators.detector import detect_validators
from commit_polish.hook import get_staged_diff, run_hook
from commit_polish.ai_service import AIServiceError

app = typer.Typer(
    name="commit-polish",
    help="AI-powered commit message rewriter.",
    add_completion=False,
)
config_app = typer.Typer(help="Manage commit-polish configuration.")
app.add_typer(config_app, name="config")

console = Console()
err_console = Console(stderr=True)


# ── hook command ─────────────────────────────────────────────────────────────

@app.command("hook")
def hook_command(
    commit_msg_file: str = typer.Argument(..., help="Path to the commit message file"),
) -> None:
    """Run as a prepare-commit-msg hook. Called automatically by pre-commit."""
    sys.exit(run_hook(commit_msg_file))


# ── preview command ──────────────────────────────────────────────────────────

@app.command("preview")
def preview_command(
    message: Optional[str] = typer.Option(
        None, "--message", "-m", help="Draft commit message (defaults to empty)"
    ),
    diff_file: Optional[Path] = typer.Option(
        None, "--diff", "-d", help="Read diff from file instead of git staged changes"
    ),
    show_diff: bool = typer.Option(
        False, "--show-diff", help="Print the diff alongside the result"
    ),
    config_path: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to config file"
    ),
) -> None:
    """Preview what commit-polish would generate for your current staged changes.

    This is the killer feature: run it before committing to see the polished
    message without making a commit. Great for iterating on your diff.

    Examples:
        commit-polish preview
        commit-polish preview --message "wip add button"
        commit-polish preview --diff changes.patch --show-diff
    """
    config = load_config(config_path)

    # Gather the diff
    if diff_file:
        if not diff_file.exists():
            err_console.print(f"[red]Error:[/red] diff file not found: {diff_file}")
            raise typer.Exit(1)
        diff = diff_file.read_text()
    else:
        diff = get_staged_diff()

    draft = message or ""

    if not diff and not draft:
        console.print(
            Panel(
                "[yellow]No staged changes found and no message provided.[/yellow]\n"
                "Stage some changes with [bold]git add[/bold] first, or pass "
                "[bold]--message[/bold] / [bold]--diff[/bold].",
                title="[bold]commit-polish preview[/bold]",
                border_style="yellow",
            )
        )
        raise typer.Exit(0)

    # Show inputs
    if show_diff and diff:
        console.print(
            Panel(
                Syntax(diff[:3000] + ("..." if len(diff) > 3000 else ""), "diff", line_numbers=False),
                title="[dim]Staged diff[/dim]",
                border_style="dim",
            )
        )

    if draft:
        console.print(f"[dim]Draft message:[/dim] {draft}\n")

    validators = detect_validators(
        validator_command=config.validation.validator_command,
        auto_detect=config.validation.auto_detect,
    )

    attempts_log: list[tuple[int, str]] = []

    def on_attempt(attempt: int, msg: str) -> None:
        attempts_log.append((attempt, msg))

    result_holder: list[object] = []
    error_holder: list[Exception] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Generating commit message…", total=None)

        try:
            result = rewrite_message_sync(
                diff=diff,
                original_message=draft,
                config=config,
                validators=validators,
                on_attempt=on_attempt,
            )
            result_holder.append(result)
        except AIServiceError as e:
            error_holder.append(e)
        finally:
            progress.remove_task(task)

    if error_holder:
        console.print(
            Panel(
                f"[red]{error_holder[0]}[/red]",
                title="[bold red]LLM Unavailable[/bold red]",
                border_style="red",
            )
        )
        raise typer.Exit(1)

    result = result_holder[0]  # type: ignore[assignment]

    # Show retry attempts if there were multiple
    if result.attempts > 1:  # type: ignore[union-attr]
        console.print(f"[dim]Validation required {result.attempts} attempt(s).[/dim]\n")  # type: ignore[union-attr]

    # Show the polished message
    console.print(
        Panel(
            f"[bold green]{result.message}[/bold green]",  # type: ignore[union-attr]
            title="[bold]✓ Polished Commit Message[/bold]",
            border_style="green",
        )
    )

    if result.validation_errors:  # type: ignore[union-attr]
        console.print(
            Panel(
                "\n".join(f"• {e}" for e in result.validation_errors),  # type: ignore[union-attr]
                title="[yellow]Validation warnings (message used anyway)[/yellow]",
                border_style="yellow",
            )
        )

    # Show model/config info
    _table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    _table.add_column(style="dim")
    _table.add_column()
    _table.add_row("model", config.ai.model)
    _table.add_row("temperature", str(config.ai.temperature))
    _table.add_row("validators", str(len(validators)) if validators else "none")
    console.print(_table)


# ── test command ─────────────────────────────────────────────────────────────

@app.command("test")
def test_command(
    message: str = typer.Option("", "--message", "-m", help="Draft commit message"),
    diff_file: Optional[Path] = typer.Option(
        None, "--diff", "-d", help="Path to diff file"
    ),
    config_path: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to config file"
    ),
) -> None:
    """Test commit-polish with explicit inputs (no git repo needed).

    Useful for CI, scripting, or trying out different messages.

    Example:
        commit-polish test --message "fix stuff" --diff my.patch
    """
    # Reuse preview logic with explicit inputs
    ctx = typer.get_current_context()
    ctx.invoke(
        preview_command,
        message=message or None,
        diff_file=diff_file,
        show_diff=True,
        config_path=config_path,
    )


# ── config subcommands ────────────────────────────────────────────────────────

@config_app.command("init")
def config_init(
    path: Optional[Path] = typer.Option(
        None, "--path", help="Write config to this path instead of default"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing config"),
) -> None:
    """Write a default config file to ~/.config/commit-polish/config.toml."""
    target = path or DEFAULT_CONFIG_PATH

    if target.exists() and not force:
        console.print(f"[yellow]Config already exists at {target}[/yellow]")
        console.print("Use [bold]--force[/bold] to overwrite.")
        raise typer.Exit(0)

    written = write_default_config(target)
    console.print(f"[green]✓ Config written to {written}[/green]")
    console.print(f"\nEdit it to set your llamafile path and model.")


@config_app.command("show")
def config_show(
    path: Optional[Path] = typer.Option(None, "--path", help="Path to config file"),
) -> None:
    """Show the current configuration."""
    config_path = path or DEFAULT_CONFIG_PATH

    if not config_path.exists():
        console.print(f"[yellow]No config found at {config_path}[/yellow]")
        console.print("Run [bold]commit-polish config init[/bold] to create one.")
        raise typer.Exit(0)

    config = load_config(config_path)

    table = Table(title=f"Config: {config_path}", box=box.ROUNDED)
    table.add_column("Section", style="bold")
    table.add_column("Key")
    table.add_column("Value")

    table.add_row("ai", "model", config.ai.model)
    table.add_row("ai", "temperature", str(config.ai.temperature))
    table.add_row("ai", "max_tokens", str(config.ai.max_tokens))
    table.add_row("ai", "api_base", config.ai.api_base)
    table.add_row("llamafile", "path", config.llamafile.path or "[dim]not set[/dim]")
    table.add_row("llamafile", "model_path", config.llamafile.model_path or "[dim]not set[/dim]")
    table.add_row("validation", "auto_detect", str(config.validation.auto_detect))
    table.add_row("validation", "max_retries", str(config.validation.max_retries))

    console.print(table)


def main() -> None:
    app()
