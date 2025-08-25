"""
Command-line interface for commitgen tool.
"""

import click
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..shared.config import Config
from .git import CommitGenGitService
from .generator import CommitGenerator
from ..changelog import ChangelogGenerator
from ..shared.git import GitService
import os

console = Console()


@click.group()
def cli():
    """Generate commit messages and changelogs using AI."""
    pass


@cli.command()
@click.option(
    "--files",
    "-f",
    multiple=True,
    help="Specific files to generate commit messages for",
)
@click.option("--repo", "-r", help="Repository path")
@click.option("--commit", "-c", is_flag=True, help="Automatically commit changes")
@click.option("--push", "-p", is_flag=True, help="Push changes after commit")
@click.option(
    "--conventional/--no-conventional",
    default=True,
    help="Use conventional commit format",
)
@click.option("--no-stage", is_flag=True, help="Skip automatic staging of changes")
@click.option("--sign", is_flag=True, help="Sign commits with GPG")
@click.option("--temperature", type=float, help="AI temperature (0.0-1.0)")
@click.option(
    "--emoji/--no-emoji",
    default=False,
    help="Include emoji prefixes in commit messages",
)
@click.option(
    "--smart-group/--per-file",
    default=True,
    help="Smartly group multiple file changes into one commit (disable to commit per-file)",
)
@click.option("--no-verify", is_flag=True, help="Bypass git hooks when committing")
def generate(
    files: tuple,
    repo: str,
    commit: bool,
    push: bool,
    conventional: bool,
    no_stage: bool,
    sign: bool,
    temperature: float,
    emoji: bool,
    smart_group: bool,
    no_verify: bool,
):
    """Generate commit messages for staged changes"""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Initialize services
            config = Config()
            # Override emoji setting for this invocation without persisting to disk
            config._config["emoji"] = "true" if emoji else "false"
            git_service = CommitGenGitService(config)
            ai_service = CommitGenerator(config)

            # Stage all changes if not disabled
            if not no_stage:
                task = progress.add_task("Staging changes...", total=None)
                git_service.stage_all_changes()
                progress.update(task, completed=True)

            # Get staged changes
            task = progress.add_task("Analyzing changes...", total=None)
            staged_changes = git_service.get_staged_changes(files)
            progress.update(task, completed=True)

            if not staged_changes:
                console.print("[yellow]No staged changes found.[/yellow]")
                return

            # Generate commit message(s)
            task = progress.add_task("Generating commit message...", total=None)
            messages_by_file = None
            if smart_group:
                commit_message = ai_service.generate_commit_message(
                    staged_changes, temperature
                )
            else:
                diffs_map = git_service.get_staged_changes_map(
                    list(files) if files else None
                )
                messages_by_file = ai_service.generate_batch_messages(
                    diffs_map, temperature
                )
                commit_message = None
            progress.update(task, completed=True)

            # Show preview and confirm
            console.print("\n[bold]Generated commit message(s):[/bold]")
            if messages_by_file:
                for fp, msg in messages_by_file.items():
                    console.print(
                        Panel(f"{fp}\n\n{msg}", title="Preview", border_style="blue")
                    )
            else:
                console.print(
                    Panel(commit_message, title="Preview", border_style="blue")
                )

            if commit:
                task = progress.add_task("Committing changes...", total=None)
                if messages_by_file:
                    # Commit each file separately with its message
                    # Ensure only that file is included in the commit by using pathspec
                    # Assumes files are already staged; git commit -- <file> will include only that path
                    for fp, msg in messages_by_file.items():
                        ok, out, err, code = git_service.commit_paths_verbose(
                            msg, [fp], sign=sign, no_verify=no_verify
                        )
                        if not ok:
                            raise Exception(
                                f"Failed to commit {fp}: {err or out or code}"
                            )
                else:
                    if no_verify:
                        ok, out, err, code = git_service.commit_verbose(
                            commit_message, sign=sign, no_verify=True
                        )
                        if not ok:
                            raise Exception(f"Failed to commit: {err or out or code}")
                    else:
                        git_service.commit_changes(commit_message, sign=sign)
                progress.update(task, completed=True)

                if push:
                    task = progress.add_task("Pushing changes...", total=None)
                    git_service.push_changes()
                    progress.update(task, completed=True)

                console.print("[green]Changes committed successfully![/green]")
            else:
                console.print(
                    "[yellow]Use --commit to apply the commit message.[/yellow]"
                )

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise click.Abort()


@cli.group()
def changelog():
    """Generate and manage changelogs"""
    pass


@changelog.command(name="generate")
@click.option(
    "--version", "-v", required=True, help="Version number for the changelog entry"
)
@click.option("--from-tag", "-t", help="Generate changelog from this tag")
@click.option("--days", "-d", type=int, help="Generate changelog from the last N days")
@click.option(
    "--commits", "-n", type=int, help="Generate changelog from the last N commits"
)
@click.option("--output", "-o", help="Output file path (default: CHANGELOG.md)")
@click.option("--temperature", type=float, help="AI temperature (0.0-1.0)")
def generate_log(
    version: str,
    from_tag: str,
    days: int,
    commits: int,
    output: str,
    temperature: float,
):
    """Generate a changelog from git history"""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Initialize services
            config = Config()
            git_service = CommitGenGitService(config)
            changelog_gen = ChangelogGenerator(config, git_service)

            task = progress.add_task("Analyzing commit history...", total=None)

            # Determine which method to use for getting commits
            if from_tag:
                entries = changelog_gen.get_commits(from_tag)
            elif days:
                entries = changelog_gen.get_commits_since_date(days)
            elif commits:
                entries = changelog_gen.get_last_n_commits(commits)
            else:
                # Default: get commits from the last 7 days
                entries = changelog_gen.get_commits_since_date(7)

            progress.update(task, completed=True)

            if not entries:
                console.print(
                    "[yellow]No conventional commits found in the specified range.[/yellow]"
                )
                return

            task = progress.add_task("Generating changelog...", total=None)
            output_path = output if output else "CHANGELOG.md"
            changelog_gen.update_changelog_file(version, entries, output_path)
            progress.update(task, completed=True)

            console.print(
                f"[green]Changelog generated successfully at {output_path}![/green]"
            )

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise click.Abort()


@cli.group()
def config():
    """Manage configuration"""
    pass


@config.command()
@click.option("--key", "-k", required=True, help="Configuration key")
@click.option("--value", "-v", required=True, help="Configuration value")
def set(key: str, value: str):
    """Set configuration value"""
    try:
        config = Config()
        config.set(key, value)
        console.print(f"[green]Configuration updated: {key}={value}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise click.Abort()


@config.command()
def show():
    """Show current configuration"""
    try:
        config = Config()
        console.print(
            Panel(
                "\n".join(f"{k}: {v}" for k, v in config.get_all().items()),
                title="[blue]Current Configuration[/blue]",
                border_style="blue",
            )
        )
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise click.Abort()


@cli.command()
def status():
    """Show the current state of the repository."""
    try:
        # Initialize services
        git = GitService(os.getcwd())

        # Get repository info
        repo_name = git.get_repo_name()
        current_branch = git.get_current_branch()

        # Get changes
        staged_files = git.get_staged_files()
        unstaged_files = git.get_unstaged_files()

        # Create status table
        table = Table(title=f"Repository Status: {repo_name} ({current_branch})")
        table.add_column("Status", style="cyan")
        table.add_column("Files", style="green")

        # Add staged changes
        if staged_files:
            staged_content = "\n".join(f"  • {file}" for file in staged_files)
            table.add_row("Staged", staged_content)
        else:
            table.add_row("Staged", "No staged changes")

        # Add unstaged changes
        if unstaged_files:
            unstaged_content = "\n".join(f"  • {file}" for file in unstaged_files)
            table.add_row("Unstaged", unstaged_content)
        else:
            table.add_row("Unstaged", "No unstaged changes")

        # Show status
        console.print("\n[bold]Repository Status:[/bold]")
        console.print(table)

        # Show diffs if there are changes
        if staged_files or unstaged_files:
            console.print("\n[bold]Changes:[/bold]")

            # Show staged diffs
            if staged_files:
                console.print("\n[cyan]Staged Changes:[/cyan]")
                for file in staged_files:
                    diff = git.get_diff(file, staged=True)
                    if diff:
                        console.print(Syntax(diff, "diff", theme="monokai"))

            # Show unstaged diffs
            if unstaged_files:
                console.print("\n[yellow]Unstaged Changes:[/yellow]")
                for file in unstaged_files:
                    diff = git.get_diff(file, staged=False)
                    if diff:
                        console.print(Syntax(diff, "diff", theme="monokai"))

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise click.Abort()


# Add command aliases
cli.add_command(generate, name="g")
cli.add_command(config, name="c")
cli.add_command(changelog, name="log")

if __name__ == "__main__":
    cli()
