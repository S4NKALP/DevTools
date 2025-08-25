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

        raw = self.generate_completion(
            system_prompt, user_prompt, temperature=temperature
        )
        return self._clean_changelog_content(raw, version)

    def _clean_changelog_content(self, text: str, version: str) -> str:
        """Sanitize AI output to avoid nested headers and code fences.

        - Remove triple backtick fences
        - Remove duplicate version headers inside content (e.g., '## v1.2.3')
        - Trim excess surrounding whitespace
        """
        cleaned = text.replace("```", "").strip()
        # Drop any inner version headers
        normalized_version = version.lstrip("vV")
        inner_header_pattern = rf"^##\s+v?{re.escape(normalized_version)}\s*$"
        lines = []
        for line in cleaned.splitlines():
            if re.match(inner_header_pattern, line.strip()):
                continue
            lines.append(line)
        return "\n".join(lines).strip()

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

        # Normalize and prepare new entry
        normalized_version = version.lstrip("vV")
        header_line = f"## v{normalized_version}"
        new_version_entry = f"{header_line}\n\n{changelog_content}\n\n"

        content = existing_content or ""

        # Ensure a single top-level title
        if not content.strip():
            content = f"# Changelog\n\n{new_version_entry}"
        else:
            # Remove duplicate top-level titles that might exist mid-file
            lines = content.splitlines()
            cleaned_lines = []
            for i, line in enumerate(lines):
                if i != 0 and line.strip() == "# Changelog":
                    # skip duplicate title
                    continue
                cleaned_lines.append(line)
            content = "\n".join(cleaned_lines)

            # Ensure the file starts with a single title
            if not content.lstrip().startswith(
                "# Changelog\n"
            ) and not content.strip().startswith("# Changelog"):
                content = f"# Changelog\n\n{content.strip()}\n"

            # Replace existing section for this version (match both with and without leading 'v')
            # Find a header line matching the version
            pattern = (
                rf"^##\s+v?{re.escape(normalized_version)}\s*$[\s\S]*?(?=^##\s+|\Z)"
            )
            if re.search(pattern, content, flags=re.MULTILINE):
                content = re.sub(
                    pattern, new_version_entry, content, flags=re.MULTILINE
                )
            else:
                # Insert new entry after the title
                if content.startswith("# Changelog\n\n"):
                    content = content.replace(
                        "# Changelog\n\n", f"# Changelog\n\n{new_version_entry}", 1
                    )
                else:
                    # Fallback: prepend
                    content = f"# Changelog\n\n{new_version_entry}{content}"

        # Write updated changelog
        with open(output_file, "w") as f:
            f.write(content)

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
