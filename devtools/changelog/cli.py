"""
Changelog generation CLI.
"""
import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from .generator import ChangelogGenerator
from ..commitgen.config import CommitGenConfig

console = Console()

@click.group()
def cli():
    """Generate changelogs."""
    pass

@cli.command()
@click.option("--version", "-v", required=True, help="Version number")
@click.option("--output", "-o", default="CHANGELOG.md", help="Output file path")
@click.option("--temperature", "-t", type=float, default=0.7, help="AI temperature")
def generate(version: str, output: str, temperature: float):
    """Generate a changelog interactively."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        # Initialize services
        progress.add_task("Initializing...", total=None)
        config = CommitGenConfig()
        generator = ChangelogGenerator(config)
        
        # Collect changes
        console.print("\n[bold]Enter your changes (one per line). Start each line with an emoji to indicate the type:[/]")
        console.print("✨ Added")
        console.print("🔄 Changed")
        console.print("🐛 Fixed")
        console.print("🚀 Performance")
        console.print("📝 Documentation")
        console.print("🔧 Maintenance")
        console.print("🗑️ Removed")
        console.print("🔒 Security")
        console.print("\nPress Ctrl+D (Unix) or Ctrl+Z (Windows) when done.\n")
        
        changes_text = []
        while True:
            try:
                line = Prompt.ask("")
                if line:
                    changes_text.append(line)
            except EOFError:
                break
                
        if not changes_text:
            console.print("[yellow]No changes provided. Exiting.")
            return
            
        # Parse changes
        progress.add_task("Parsing changes...", total=None)
        changes = generator.parse_changes_from_text("\n".join(changes_text))
        
        # Generate changelog
        progress.add_task("Generating changelog...", total=None)
        generator.update_changelog_file(version, changes, output, temperature)
        
        console.print(f"\n[green]Generated changelog at {output}")

@cli.command()
@click.option("--version", "-v", required=True, help="Version number")
@click.option("--input", "-i", required=True, help="Input file with changes")
@click.option("--output", "-o", default="CHANGELOG.md", help="Output file path")
@click.option("--temperature", "-t", type=float, default=0.7, help="AI temperature")
def generate_from_file(version: str, input: str, output: str, temperature: float):
    """Generate a changelog from a file."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        # Initialize services
        progress.add_task("Initializing...", total=None)
        config = CommitGenConfig()
        generator = ChangelogGenerator(config)
        
        # Read changes from file
        progress.add_task("Reading changes...", total=None)
        try:
            with open(input, "r") as f:
                changes_text = f.read()
        except FileNotFoundError:
            console.print(f"[red]Input file not found: {input}")
            return
            
        # Parse changes
        progress.add_task("Parsing changes...", total=None)
        changes = generator.parse_changes_from_text(changes_text)
        
        if not changes:
            console.print("[yellow]No changes found in input file.")
            return
            
        # Generate changelog
        progress.add_task("Generating changelog...", total=None)
        generator.update_changelog_file(version, changes, output, temperature)
        
        console.print(f"\n[green]Generated changelog at {output}")

# Add command aliases
cli.add_command(generate, name="g")
cli.add_command(generate_from_file, name="f") 