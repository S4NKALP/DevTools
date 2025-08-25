"""
Main CLI for devtools.
"""

import click
from rich.console import Console
from rich.table import Table
from .shared.config import Config
from .gitignore.cli import cli as gitignore_cli
from .commitgen.cli import cli as commit_cli
from .licensegen.cli import license as license_cli
from .hooks.cli import cli as hooks_cli
from .changelog.cli import cli as changelog_cli

console = Console()


@click.group()
def cli():
    """DevTools - A collection of developer tools."""
    pass


@cli.group()
def config():
    """Manage configuration."""
    pass


@config.command()
@click.argument("key")
@click.argument("value")
def set(key: str, value: str):
    """Set a configuration value."""
    config = Config()
    config.set(key, value)
    console.print(f"[green]Set {key} to {value}")


@config.command()
@click.argument("key", required=False)
def show(key: str = None):
    """Show configuration values."""
    config = Config()
    if key:
        value = config.get(key)
        if value is None:
            console.print(f"[yellow]No value set for {key}")
        else:
            console.print(f"{key}: {value}")
    else:
        table = Table(title="Configuration")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")

        for k, v in config.get_all().items():
            table.add_row(k, str(v))

        console.print(table)


@config.command()
@click.argument("key")
def delete(key: str):
    """Delete a configuration value."""
    config = Config()
    if key in config.get_all():
        config.delete(key)
        console.print(f"[green]Deleted {key}")
    else:
        console.print(f"[yellow]No value set for {key}")


@config.command()
def clear():
    """Clear all configuration values."""
    if click.confirm("Are you sure you want to clear all configuration?"):
        config = Config()
        config.clear()
        console.print("[green]Cleared all configuration")


# Add subcommands
cli.add_command(commit_cli, name="commit")
cli.add_command(changelog_cli, name="changelog")
cli.add_command(gitignore_cli, name="gitignore")
cli.add_command(license_cli, name="license")
cli.add_command(hooks_cli, name="hooks")

if __name__ == "__main__":
    cli()
