"""
Gitignore generation CLI.
"""

import os
import click
from rich.console import Console
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from .generator import GitignoreGenerator
from .detector import ProjectDetector

console = Console()


@click.group()
def cli():
    """Generate .gitignore files."""
    pass


@cli.command()
@click.option("--directory", "-d", default=".", help="Directory to scan")
@click.option("--output", "-o", default=".gitignore", help="Output file path")
def auto(directory: str, output: str):
    """Automatically detect project types and generate .gitignore."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Initialize services
        progress.add_task("Initializing...", total=None)
        detector = ProjectDetector(directory)
        generator = GitignoreGenerator()

        # Detect project types
        progress.add_task("Detecting project types...", total=None)
        detected_types = detector.detect_project_types()

        if not detected_types:
            console.print(
                "[yellow]No project types detected. Using generic .gitignore."
            )
        else:
            console.print(
                f"\n[green]Detected project types:[/] {', '.join(detected_types)}"
            )

        # Check if output file exists
        if os.path.exists(output):
            if not Confirm.ask(f"\n[yellow]File {output} already exists. Overwrite?"):
                return

        # Generate .gitignore
        progress.add_task("Generating .gitignore...", total=None)
        generator.update_gitignore_file(detected_types, output)

        console.print(f"\n[green]Generated .gitignore at {output}")


@cli.command()
@click.argument("types", nargs=-1, required=True)
@click.option("--output", "-o", default=".gitignore", help="Output file path")
def generate(types: tuple, output: str):
    """Generate .gitignore for specified types."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Initialize services
        progress.add_task("Initializing...", total=None)
        generator = GitignoreGenerator()

        # Check if output file exists
        if os.path.exists(output):
            if not Confirm.ask(f"\n[yellow]File {output} already exists. Overwrite?"):
                return

        # Generate .gitignore
        progress.add_task("Generating .gitignore...", total=None)
        generator.update_gitignore_file(list(types), output)

        console.print(f"\n[green]Generated .gitignore at {output}")


# Add command aliases
cli.add_command(auto, name="a")
cli.add_command(generate, name="g")

if __name__ == "__main__":
    cli()
