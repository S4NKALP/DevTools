"""
Changelog generation CLI.
"""

import os
import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from .generator import ChangelogGenerator
from ..shared.config import Config

console = Console()


@click.group()
def cli():
    """Generate changelogs."""
    pass


@cli.command()
@click.option(
    "--version", "-v", required=True, help="Version number for the changelog entry"
)
@click.option("--from-tag", "-t", help="Generate changelog from this tag")
@click.option("--days", "-d", type=int, help="Generate changelog from the last N days")
@click.option(
    "--commits", "-n", type=int, help="Generate changelog from the last N commits"
)
@click.option("--output", "-o", default="CHANGELOG.md", help="Output file path")
@click.option("--temperature", type=float, default=0.7, help="AI temperature (0.0-1.0)")
def generate(
    version: str,
    from_tag: str,
    days: int,
    commits: int,
    output: str,
    temperature: float,
):
    """Generate a changelog from git history."""
    try:
        # Get configuration
        config = Config()

        # Validate version format
        if not version.startswith("v"):
            version = f"v{version}"

        # Get git history
        if from_tag:
            # Get commits since tag
            cmd = f"git log {from_tag}..HEAD --pretty=format:%s"
        elif days:
            # Get commits from last N days
            cmd = f"git log --since='{days} days ago' --pretty=format:%s"
        elif commits:
            # Get last N commits
            cmd = f"git log -n {commits} --pretty=format:%s"
        else:
            # Get all commits
            cmd = "git log --pretty=format:%s"

        # Execute git command
        result = os.popen(cmd).read().strip()
        if not result:
            console.print("[yellow]No commits found in the specified range")
            return

        # Split into individual commits
        commit_messages = [msg.strip() for msg in result.split("\n") if msg.strip()]

        # Group commits by type
        groups = {
            "✨ Added": [],
            "🔄 Changed": [],
            "🐛 Fixed": [],
            "🚀 Performance": [],
            "📝 Documentation": [],
            "🔧 Maintenance": [],
            "🗑️ Removed": [],
            "🔒 Security": [],
        }

        # Map commit types to groups
        type_map = {
            "feat": "✨ Added",
            "add": "✨ Added",
            "new": "✨ Added",
            "change": "🔄 Changed",
            "update": "🔄 Changed",
            "fix": "🐛 Fixed",
            "bug": "🐛 Fixed",
            "perf": "🚀 Performance",
            "docs": "📝 Documentation",
            "chore": "🔧 Maintenance",
            "refactor": "🔧 Maintenance",
            "remove": "🗑️ Removed",
            "delete": "🗑️ Removed",
            "security": "🔒 Security",
        }

        # Categorize commits
        for msg in commit_messages:
            msg_lower = msg.lower()
            categorized = False

            # Check for type prefixes
            for type_key, group in type_map.items():
                if msg_lower.startswith(type_key):
                    groups[group].append(msg)
                    categorized = True
                    break

            # If not categorized, check for keywords
            if not categorized:
                for type_key, group in type_map.items():
                    if type_key in msg_lower:
                        groups[group].append(msg)
                        break
                else:
                    # Default to maintenance if no match
                    groups["🔧 Maintenance"].append(msg)

        # Generate changelog
        changelog = f"# Changelog\n\n## {version}\n\n"

        # Add each group
        for group, messages in groups.items():
            if messages:
                changelog += f"### {group}\n\n"
                for msg in messages:
                    changelog += f"- {msg}\n"
                changelog += "\n"

        # Write to file
        with open(output, "w") as f:
            f.write(changelog)

        console.print(f"[green]✓[/green] Changelog generated successfully at: {output}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


@cli.command()
@click.option(
    "--version", "-v", required=True, help="Version number for the changelog entry"
)
@click.option("--output", "-o", default="CHANGELOG.md", help="Output file path")
@click.option("--temperature", type=float, default=0.7, help="AI temperature (0.0-1.0)")
def generate_interactive(version: str, output: str, temperature: float):
    """Generate a changelog interactively."""
    try:
        # Get configuration
        config = Config()

        # Validate version format
        if not version.startswith("v"):
            version = f"v{version}"

        # Initialize groups
        groups = {
            "✨ Added": [],
            "🔄 Changed": [],
            "🐛 Fixed": [],
            "🚀 Performance": [],
            "📝 Documentation": [],
            "🔧 Maintenance": [],
            "🗑️ Removed": [],
            "🔒 Security": [],
        }

        console.print(
            "\n[bold cyan]Enter your changes (press Enter twice to finish):[/bold cyan]"
        )
        console.print("[dim]Start each line with an emoji to categorize it:[/dim]")
        console.print("✨ - Added")
        console.print("🔄 - Changed")
        console.print("🐛 - Fixed")
        console.print("🚀 - Performance")
        console.print("📝 - Documentation")
        console.print("🔧 - Maintenance")
        console.print("🗑️ - Removed")
        console.print("🔒 - Security")
        console.print("\n[dim]Example: ✨ Added new feature X[/dim]\n")

        while True:
            line = click.prompt("", default="", show_default=False)
            if not line:
                break

            # Categorize based on emoji
            for group in groups:
                if line.startswith(group.split()[0]):
                    groups[group].append(line)
                    break
            else:
                # Default to maintenance if no emoji
                groups["🔧 Maintenance"].append(line)

        # Generate changelog
        changelog = f"# Changelog\n\n## {version}\n\n"

        # Add each group
        for group, messages in groups.items():
            if messages:
                changelog += f"### {group}\n\n"
                for msg in messages:
                    changelog += f"- {msg}\n"
                changelog += "\n"

        # Write to file
        with open(output, "w") as f:
            f.write(changelog)

        console.print(f"[green]✓[/green] Changelog generated successfully at: {output}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


@cli.command()
@click.option(
    "--version", "-v", required=True, help="Version number for the changelog entry"
)
@click.option("--input", "-i", required=True, help="Input file with changes")
@click.option("--output", "-o", default="CHANGELOG.md", help="Output file path")
@click.option("--temperature", type=float, default=0.7, help="AI temperature (0.0-1.0)")
def generate_from_file(version: str, input: str, output: str, temperature: float):
    """Generate a changelog from a file."""
    try:
        # Get configuration
        config = Config()

        # Validate version format
        if not version.startswith("v"):
            version = f"v{version}"

        # Read input file
        with open(input, "r") as f:
            changes = f.read().strip()

        if not changes:
            console.print("[yellow]No changes found in input file")
            return

        # Split into lines
        lines = [line.strip() for line in changes.split("\n") if line.strip()]

        # Initialize groups
        groups = {
            "✨ Added": [],
            "🔄 Changed": [],
            "🐛 Fixed": [],
            "🚀 Performance": [],
            "📝 Documentation": [],
            "🔧 Maintenance": [],
            "🗑️ Removed": [],
            "🔒 Security": [],
        }

        # Categorize changes
        for line in lines:
            line_lower = line.lower()
            categorized = False

            # Check for emoji prefixes
            for group in groups:
                if line.startswith(group.split()[0]):
                    groups[group].append(line)
                    categorized = True
                    break

            # If not categorized, check for keywords
            if not categorized:
                type_map = {
                    "add": "✨ Added",
                    "new": "✨ Added",
                    "change": "🔄 Changed",
                    "update": "🔄 Changed",
                    "fix": "🐛 Fixed",
                    "bug": "🐛 Fixed",
                    "perf": "🚀 Performance",
                    "docs": "📝 Documentation",
                    "chore": "🔧 Maintenance",
                    "refactor": "🔧 Maintenance",
                    "remove": "🗑️ Removed",
                    "delete": "🗑️ Removed",
                    "security": "🔒 Security",
                }

                for type_key, group in type_map.items():
                    if type_key in line_lower:
                        groups[group].append(line)
                        break
                else:
                    # Default to maintenance if no match
                    groups["🔧 Maintenance"].append(line)

        # Generate changelog
        changelog = f"# Changelog\n\n## {version}\n\n"

        # Add each group
        for group, messages in groups.items():
            if messages:
                changelog += f"### {group}\n\n"
                for msg in messages:
                    changelog += f"- {msg}\n"
                changelog += "\n"

        # Write to file
        with open(output, "w") as f:
            f.write(changelog)

        console.print(f"[green]✓[/green] Changelog generated successfully at: {output}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


# Add command aliases
cli.add_command(generate, name="g")
cli.add_command(generate_interactive, name="i")
cli.add_command(generate_from_file, name="f")

if __name__ == "__main__":
    cli()
