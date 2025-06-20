"""
Changelog generation using AI.
"""

from typing import List, Dict, Optional
from ..shared.ai import AIService
from ..shared.config import Config
from ..shared.git import GitService
import re


class ChangelogGenerator(AIService):
    """AI-powered changelog generator."""

    def __init__(self, config: Config, git_service: Optional[GitService] = None):
        """Initialize changelog generator.

        Args:
            config: Configuration object
            git_service: Optional GitService instance
        """
        super().__init__(config)
        self.git_service = git_service

    def get_commits(self, from_tag: str) -> List[Dict[str, str]]:
        """Get commits since a tag."""
        if not self.git_service:
            raise ValueError("GitService not provided")
        return self.git_service.get_commits_since_tag(from_tag)

    def get_commits_since_date(self, days: int) -> List[Dict[str, str]]:
        """Get commits since a date."""
        if not self.git_service:
            raise ValueError("GitService not provided")
        return self.git_service.get_commits_since_date(days)

    def get_last_n_commits(self, n: int) -> List[Dict[str, str]]:
        """Get last N commits."""
        if not self.git_service:
            raise ValueError("GitService not provided")
        return self.git_service.get_commit_history(limit=n)

    def _extract_pr_reference(self, message: str) -> Optional[str]:
        """Extract PR reference from commit message if it exists."""
        # Look for patterns like (#123) or (#123, #456)
        pr_pattern = r"\(#(\d+)(?:,\s*#\d+)*\)"
        match = re.search(pr_pattern, message)
        if match:
            # Return the full match including parentheses
            return match.group(0)
        return None

    def generate_changelog(
        self,
        version: str,
        changes: List[Dict[str, str]],
        temperature: Optional[float] = None,
    ) -> str:
        """Generate a changelog from a list of changes.

        Args:
            version: Version number for the changelog
            changes: List of changes, each with 'message' and 'hash'
            temperature: AI temperature for generation

        Returns:
            Generated changelog content
        """
        system_prompt = """You are a helpful AI that generates changelogs.
        Follow these rules:
        1. Group changes by type (Added, Changed, Fixed, etc.)
        2. Keep descriptions concise but informative
        3. Use past tense
        4. Start each entry with a verb
        5. Use emojis for each type:
           - ✨ Added
           - 🔄 Changed
           - 🐛 Fixed
           - 🚀 Performance
           - 📝 Documentation
           - 🔧 Maintenance
           - 🗑️ Removed
           - 🔒 Security
        6. Only include PR references if they exist in the original commit message
        7. Keep the changelog clean and professional"""

        # Format changes for the prompt, preserving PR references
        changes_text = "\n".join(f"{change['message']}" for change in changes)

        user_prompt = f"Generate a changelog for version {
            version
        } with these changes:\n\n{changes_text}"

        return self.generate_completion(
            system_prompt, user_prompt, temperature=temperature
        )

    def update_changelog_file(
        self,
        version: str,
        changes: List[Dict[str, str]],
        output_file: str,
        temperature: Optional[float] = None,
    ) -> None:
        """Generate and update a changelog file.

        Args:
            version: Version number for the changelog
            changes: List of changes, each with 'message' and 'hash'
            output_file: Path to the changelog file
            temperature: AI temperature for generation
        """
        changelog_content = self.generate_changelog(version, changes, temperature)

        # Read existing changelog if it exists
        try:
            with open(output_file, "r") as f:
                existing_content = f.read()
        except FileNotFoundError:
            existing_content = ""

        # Create new version entry
        new_version_entry = f"## {version}\n\n{changelog_content}\n\n"

        if existing_content:
            # Check if version already exists
            version_pattern = f"## {version}\n"
            if version_pattern in existing_content:
                # Replace existing version content
                pattern = f"{version_pattern}.*?(?=## |$)"
                new_content = re.sub(
                    pattern, new_version_entry, existing_content, flags=re.DOTALL
                )
            else:
                # Add new version at the top
                new_content = new_version_entry + existing_content
        else:
            # Create new changelog
            new_content = f"# Changelog\n\n{new_version_entry}"

        # Write updated changelog
        with open(output_file, "w") as f:
            f.write(new_content)

    def parse_changes_from_text(self, text: str) -> List[Dict[str, str]]:
        """Parse changes from text input.

        Args:
            text: Text containing changes

        Returns:
            List of changes with type and description
        """
        changes = []
        current_type = None
        current_description = []

        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue

            # Check if line starts with a type marker
            type_markers = {
                "✨": "Added",
                "🔄": "Changed",
                "🐛": "Fixed",
                "🚀": "Performance",
                "📝": "Documentation",
                "🔧": "Maintenance",
                "🗑️": "Removed",
                "🔒": "Security",
            }

            for marker, type_ in type_markers.items():
                if line.startswith(marker):
                    # Save previous change if exists
                    if current_type and current_description:
                        changes.append(
                            {
                                "type": current_type,
                                "description": " ".join(current_description),
                            }
                        )

                    # Start new change
                    current_type = type_
                    current_description = [line[len(marker) :].strip()]
                    break
            else:
                # Continue current change
                if current_type:
                    current_description.append(line)

        # Add last change if exists
        if current_type and current_description:
            changes.append(
                {"type": current_type, "description": " ".join(current_description)}
            )

        return changes
