"""License generator CLI."""

import os
import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm, Prompt
from rich.panel import Panel
from ..shared.config import Config
from .generator import license_generator, generate_license
import re

console = Console()


@click.group()
def license():
    """License generation commands."""
    pass


@license.command()
@click.option("--type", "-t", help="Type of license to generate")
@click.option("--author", "-a", help="Name of the author/copyright holder")
@click.option("--year", "-y", type=int, help="Year for the copyright notice")
@click.option("--output", "-o", default="LICENSE", help="Output file path")
@click.option("--multi", "-m", is_flag=True, help="Generate multiple licenses")
def generate(type: str, author: str, year: int, output: str, multi: bool):
    """Generate a license file."""
    try:
        # If no author specified, prompt for it
        if not author:
            author = click.prompt("Enter author name")

        # Fetch available licenses
        licenses = license_generator.fetch_available_licenses()
        if not licenses:
            console.print("[yellow]No licenses available")
            return

        # Create selection table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("No.", style="dim", width=4)
        table.add_column("License Key", style="dim", width=15)
        table.add_column("Name", width=30)
        table.add_column("Permissions", width=40)

        # Add rows with numbers
        for i, license in enumerate(licenses, 1):
            table.add_row(
                str(i),
                license["key"],
                license["name"],
                format_permissions(license.get("permissions", [])),
            )

        # Display table
        console.print("\nSelect license(s) to generate:")
        console.print(table)

        if multi:
            # Get user selection for multiple licenses
            while True:
                try:
                    selection = click.prompt(
                        "Enter license numbers (e.g., 1,3,5)"
                    ).split(",")
                    selected_indices = [int(s.strip()) for s in selection if s.strip()]

                    # Validate selection
                    if not selected_indices:
                        console.print("[yellow]No licenses selected")
                        continue

                    if any(i < 1 or i > len(licenses) for i in selected_indices):
                        console.print(
                            "[red]Invalid selection. Please enter valid numbers."
                        )
                        continue

                    # Get selected licenses
                    selected_licenses = [licenses[i - 1] for i in selected_indices]

                    # Show confirmation
                    console.print("\nSelected licenses:")
                    for license in selected_licenses:
                        console.print(f"- {license['name']} ({license['key']})")

                    if Confirm.ask("\nGenerate these licenses?"):
                        break
                    else:
                        console.print("\nPlease select licenses again:")
                        continue

                except ValueError:
                    console.print(
                        "[red]Invalid input. Please enter numbers separated by commas."
                    )
                    continue
        else:
            # Get user selection for single license
            while True:
                try:
                    selection = click.prompt("Enter license number")
                    selected_index = int(selection.strip())

                    # Validate selection
                    if selected_index < 1 or selected_index > len(licenses):
                        console.print(
                            "[red]Invalid selection. Please enter a valid number."
                        )
                        continue

                    # Get selected license
                    selected_license = licenses[selected_index - 1]

                    # Show confirmation
                    console.print(
                        f"\nSelected license: {selected_license['name']} ({selected_license['key']})"
                    )

                    if Confirm.ask("\nGenerate this license?"):
                        selected_licenses = [selected_license]
                        break
                    else:
                        console.print("\nPlease select a license again:")
                        continue

                except ValueError:
                    console.print("[red]Invalid input. Please enter a number.")
                    continue

        # Generate each license
        for license in selected_licenses:
            license_type = license["key"]
            # Generate output filename
            if len(selected_licenses) == 1:
                output_file = output
            else:
                base, ext = os.path.splitext(output)
                output_file = f"{base}_{license_type}{ext}"

            try:
                output_path = generate_license(
                    license_type=license_type,
                    author=author,
                    year=year,
                    output_file=output_file,
                )
                console.print(
                    f"[green]✓[/green] Generated {license_type} license at: {output_path}"
                )
            except ValueError as e:
                console.print(
                    f"[red]Error generating {license_type} license:[/red] {str(e)}"
                )
                continue

        # Create a combined README section
        if len(selected_licenses) > 1:
            readme_path = "LICENSE.md"
            with open(readme_path, "w") as f:
                f.write("# Licenses\n\n")
                f.write("This project is licensed under multiple licenses:\n\n")
                for license in selected_licenses:
                    f.write(f"- [{license['name']}](LICENSE_{license['key']})\n")
            console.print(
                f"\n[green]✓[/green] Created license summary at: {readme_path}"
            )

    except ValueError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


@license.command()
def list():
    """List available licenses."""
    show_licenses()


def format_permissions(permissions: list) -> str:
    """Format permissions list into a readable string."""
    if not permissions:
        return "N/A"

    # Map permission keys to readable names
    permission_map = {
        "commercial-use": "Commercial Use",
        "modifications": "Modifications",
        "distribution": "Distribution",
        "private-use": "Private Use",
        "patent-use": "Patent Use",
    }

    # Convert each permission to its readable name
    readable_permissions = [
        permission_map.get(perm, perm.replace("-", " ").title()) for perm in permissions
    ]

    return ", ".join(readable_permissions)


def truncate_description(description: str, max_length: int = 60) -> str:
    """Truncate description to a maximum length and add ellipsis if needed."""
    if not description:
        return "No description available"

    # Remove HTML tags
    description = re.sub(r"<[^>]+>", "", description)

    # Remove URLs
    description = re.sub(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        "",
        description,
    )

    # Clean up whitespace
    description = " ".join(description.split())

    if len(description) <= max_length:
        return description

    # Find the last space before max_length
    last_space = description[:max_length].rfind(" ")
    if last_space == -1:
        last_space = max_length

    return description[:last_space] + "..."


def show_licenses():
    """Display available licenses in a table."""
    try:
        # Load token from config
        config = Config()
        github_token = config.get("github_token")
        if github_token:
            os.environ["GITHUB_TOKEN"] = github_token

        # Fetch available licenses
        licenses = license_generator.fetch_available_licenses()

        if not licenses:
            console.print("[yellow]No licenses available")
            return

        # Create table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("License Key", style="dim", width=15)
        table.add_column("Name", width=30)
        table.add_column("Permissions", width=40)

        # Add rows
        for license in licenses:
            table.add_row(
                license["key"],
                license["name"],
                format_permissions(license.get("permissions", [])),
            )

        # Display table
        console.print("\nAvailable Licenses:")
        console.print(table)
        console.print(
            "\nTo generate a license, use: [bold]devtools license generate[/bold]"
        )
        console.print(
            "To generate multiple licenses, use: [bold]devtools license generate --multi[/bold]"
        )

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


if __name__ == "__main__":
    license()
