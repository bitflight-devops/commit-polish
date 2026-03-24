"""CLI for commit-polish.

Commands:
  hook <file>           Run as a prepare-commit-msg hook (called by pre-commit)
  polish                Generate a commit message and optionally commit (git polish)
  preview               Preview what the hook would generate for your staged changes
  test --message --diff Test with explicit inputs (no git repo needed)
  config init           Write a default config file
  config show           Show the current configuration
  config alias          Install the 'git polish' alias
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import os
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table
from rich import box

from commit_polish.config import load_config, write_default_config, DEFAULT_CONFIG_PATH
from commit_polish.message_rewriter import rewrite_message_sync, RewriteResult
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


# ── helpers ───────────────────────────────────────────────────────────────────


def _git(*args: str) -> str:
    """Run a git command and return stdout, empty string on failure."""
    try:
        return subprocess.run(
            ["git", *args], capture_output=True, text=True, timeout=10
        ).stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def _run_rewriter(
    diff: str,
    draft: str,
    config_path: Path | None,
    extra_context: str = "",
) -> tuple[RewriteResult | None, Exception | None]:
    """Run the rewriter and return (result, error)."""
    config = load_config(config_path)
    validators = detect_validators(
        validator_command=config.validation.validator_command,
        auto_detect=config.validation.auto_detect,
    )
    result: RewriteResult | None = None
    error: Exception | None = None

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Generating commit message…", total=None)
        try:
            result = rewrite_message_sync(
                diff=diff + ("\n\n" + extra_context if extra_context else ""),
                original_message=draft,
                config=config,
                validators=validators,
            )
        except AIServiceError as e:
            error = e
        finally:
            progress.remove_task(task)

    return result, error


def _show_result(result: RewriteResult) -> None:
    """Print the polished message panel and metadata."""
    if result.attempts > 1:
        console.print(f"[dim]Validation required {result.attempts} attempt(s).[/dim]\n")

    console.print(
        Panel(
            f"[bold green]{result.message}[/bold green]",
            title="[bold]✓ Polished Commit Message[/bold]",
            border_style="green",
        )
    )

    if result.validation_errors:
        console.print(
            Panel(
                "\n".join(f"• {e}" for e in result.validation_errors),
                title="[yellow]Validation warnings (message used anyway)[/yellow]",
                border_style="yellow",
            )
        )


# ── hook command ─────────────────────────────────────────────────────────────


@app.command("hook")  # type: ignore[untyped-decorator]
def hook_command(
    commit_msg_file: str = typer.Argument(..., help="Path to the commit message file"),
    commit_source: str | None = typer.Argument(
        None, help="Commit source (message/template/merge/squash/commit)"
    ),
    commit_sha: str | None = typer.Argument(
        None, help="SHA of the commit being amended (only with 'commit' source)"
    ),
) -> None:
    """Run as a prepare-commit-msg hook. Called automatically by pre-commit."""
    sys.exit(run_hook(commit_msg_file))


# ── polish command ────────────────────────────────────────────────────────────


@app.command("polish")  # type: ignore[untyped-decorator]
def polish_command(
    message: str | None = typer.Option(
        None, "--message", "-m", help="Draft message to refine"
    ),
    config_path: Path | None = typer.Option(
        None, "--config", "-c", help="Path to config file"
    ),
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Commit without prompting"
    ),
) -> None:
    """Generate a conventional commit message from staged changes and commit.

    Shows a summary of staged changes, generates the message, then prompts:
      [Y] commit with this message
      [e] open in $EDITOR to tweak first
      [n] abort

    Install as a git alias with:
        commit-polish config alias

    Then use as:
        git add -p
        git polish
    """
    diff = get_staged_diff()
    stat = _git("diff", "--cached", "--stat")
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")

    if not diff:
        console.print(
            Panel(
                "[yellow]No staged changes.[/yellow]\n"
                "Stage changes with [bold]git add[/bold] first.",
                title="[bold]git polish[/bold]",
                border_style="yellow",
            )
        )
        raise typer.Exit(0)

    # Show what's staged
    if stat:
        console.print(Panel(stat, title=f"[dim]Staged  ({branch})[/dim]", border_style="dim"))

    # Build extra context: branch name hints at scope/feature area
    extra = f"Branch: {branch}" if branch and branch not in ("HEAD", "main", "master") else ""

    result, error = _run_rewriter(diff, message or "", config_path, extra)

    if error:
        console.print(
            Panel(
                f"[red]{error}[/red]",
                title="[bold red]LLM Unavailable[/bold red]",
                border_style="red",
            )
        )
        raise typer.Exit(1)

    assert result is not None
    _show_result(result)

    # Prompt
    if yes:
        choice = "y"
    else:
        choice = typer.prompt(
            "\n  [Y] commit  [e] edit  [n] abort",
            default="y",
        ).strip().lower()

    if choice in ("n", "q", "abort"):
        console.print("[dim]Aborted.[/dim]")
        raise typer.Exit(0)

    final_message = result.message

    if choice in ("e", "edit"):
        editor = os.environ.get("EDITOR", "vi")
        with tempfile.NamedTemporaryFile(
            suffix=".txt", mode="w", delete=False, prefix="git-polish-"
        ) as f:
            f.write(result.message + "\n")
            tmpfile = f.name
        subprocess.run([editor, tmpfile])
        final_message = Path(tmpfile).read_text().strip()
        os.unlink(tmpfile)
        if not final_message:
            console.print("[yellow]Empty message — aborted.[/yellow]")
            raise typer.Exit(0)

    proc = subprocess.run(["git", "commit", "-m", final_message])
    if proc.returncode != 0:
        raise typer.Exit(proc.returncode)


# ── preview command ──────────────────────────────────────────────────────────


@app.command("preview")  # type: ignore[untyped-decorator]
def preview_command(
    message: str | None = typer.Option(
        None, "--message", "-m", help="Draft commit message (defaults to empty)"
    ),
    diff_file: Path | None = typer.Option(
        None, "--diff", "-d", help="Read diff from file instead of git staged changes"
    ),
    show_diff: bool = typer.Option(
        False, "--show-diff", help="Print the diff alongside the result"
    ),
    config_path: Path | None = typer.Option(
        None, "--config", "-c", help="Path to config file"
    ),
) -> None:
    """Preview what commit-polish would generate for your current staged changes.

    Examples:
        commit-polish preview
        commit-polish preview --message "wip add button"
        commit-polish preview --diff changes.patch --show-diff
    """
    config = load_config(config_path)

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

    if show_diff and diff:
        console.print(
            Panel(
                Syntax(
                    diff[:3000] + ("..." if len(diff) > 3000 else ""),
                    "diff",
                    line_numbers=False,
                ),
                title="[dim]Staged diff[/dim]",
                border_style="dim",
            )
        )

    if draft:
        console.print(f"[dim]Draft message:[/dim] {draft}\n")

    result, error = _run_rewriter(diff, draft, config_path)

    if error:
        console.print(
            Panel(
                f"[red]{error}[/red]",
                title="[bold red]LLM Unavailable[/bold red]",
                border_style="red",
            )
        )
        raise typer.Exit(1)

    assert result is not None
    _show_result(result)

    _table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    _table.add_column(style="dim")
    _table.add_column()
    validators = detect_validators(
        validator_command=config.validation.validator_command,
        auto_detect=config.validation.auto_detect,
    )
    _table.add_row("model", config.ai.model)
    _table.add_row("temperature", str(config.ai.temperature))
    _table.add_row("validators", str(len(validators)) if validators else "none")
    console.print(_table)


# ── test command ─────────────────────────────────────────────────────────────


@app.command("test")  # type: ignore[untyped-decorator]
def test_command(
    message: str = typer.Option("", "--message", "-m", help="Draft commit message"),
    diff_file: Path | None = typer.Option(
        None, "--diff", "-d", help="Path to diff file"
    ),
    config_path: Path | None = typer.Option(
        None, "--config", "-c", help="Path to config file"
    ),
) -> None:
    """Test commit-polish with explicit inputs (no git repo needed).

    Example:
        commit-polish test --message "fix stuff" --diff my.patch
    """
    ctx = typer.get_current_context()
    ctx.invoke(
        preview_command,
        message=message or None,
        diff_file=diff_file,
        show_diff=True,
        config_path=config_path,
    )


# ── config subcommands ────────────────────────────────────────────────────────


@config_app.command("init")  # type: ignore[untyped-decorator]
def config_init(
    path: Path | None = typer.Option(
        None, "--path", help="Write config to this path instead of default"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing config"
    ),
) -> None:
    """Write a default config file to ~/.config/commit-polish/config.toml."""
    target = path or DEFAULT_CONFIG_PATH

    if target.exists() and not force:
        console.print(f"[yellow]Config already exists at {target}[/yellow]")
        console.print("Use [bold]--force[/bold] to overwrite.")
        raise typer.Exit(0)

    written = write_default_config(target)
    console.print(f"[green]✓ Config written to {written}[/green]")
    console.print("\nEdit it to set your llamafile path and model.")


@config_app.command("show")  # type: ignore[untyped-decorator]
def config_show(
    path: Path | None = typer.Option(None, "--path", help="Path to config file"),
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
    table.add_row(
        "llamafile", "model_path", config.llamafile.model_path or "[dim]not set[/dim]"
    )
    table.add_row("validation", "auto_detect", str(config.validation.auto_detect))
    table.add_row("validation", "max_retries", str(config.validation.max_retries))

    console.print(table)


@config_app.command("alias")  # type: ignore[untyped-decorator]
def config_alias(
    local: bool = typer.Option(
        False, "--local", help="Install in the current repo only (default: global)"
    ),
) -> None:
    """Install the 'git polish' alias.

    After running this, you can use:
        git polish
    from any repository to generate and commit a conventional commit message.
    """
    scope = "--local" if local else "--global"
    proc = subprocess.run(
        ["git", "config", scope, "alias.polish", "!commit-polish polish"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        err_console.print(f"[red]Failed to install alias:[/red] {proc.stderr.strip()}")
        raise typer.Exit(1)

    scope_label = "this repo" if local else "globally"
    console.print(f"[green]✓ Installed [bold]git polish[/bold] alias {scope_label}.[/green]")
    console.print("\nUsage:")
    console.print("  git add -p")
    console.print("  git polish")


def main() -> None:
    app()
