"""
Commit message and changelog generation using AI.
"""

from typing import List, Dict, Optional
from ..shared.ai import AIService
from ..shared.config import Config


class CommitGenerator(AIService):
    """AI-powered commit message and changelog generator."""

    def __init__(self, config: Config):
        """Initialize commit generator."""
        super().__init__(config)

    def generate_commit_message(
        self, diff: str, temperature: Optional[float] = None
    ) -> str:
        """Generate a commit message from a diff."""
        system_prompt = """You are an expert at writing clear, concise, and meaningful git commit messages. Follow these rules strictly:

2. Format: type(scope): description
   - type: One of feat, fix, docs, style, refactor, test, chore
   - scope: Optional, describes the section of the codebase affected
   - description: Clear, concise explanation of the change

3. Types and their emojis:
   - feat: ✨ (new feature or enhancement)
   - fix: 🐛 (bug fix)
   - docs: 📚 (documentation changes)
   - style: 💅 (formatting, missing semi colons, etc; no code change)
   - refactor: ♻️ (code restructuring, no functional changes)
   - test: ✅ (adding or modifying tests)
   - chore: 🔧 (maintenance tasks, dependencies, etc)

4. Guidelines:
   - Write the ENTIRE message on a single line
   - Keep the message concise and to the point
   - Use imperative mood ("add" not "added")
   - Don't end with a period
   - Focus on the "why" not the "what"
   - Be specific about the change
   - Use present tense
   - Start with a verb
   - Don't include pull request references in the main message
   - Keep the message clean and focused on the change itself
   - When analyzing multiple files, focus on the overall change and its impact
   - DO NOT include any explanatory text or "Based on the changes" phrases
   - DO NOT include file paths in the message
   - DO NOT include any text about what can be written

5. Examples:
   - ✨ feat(auth): add OAuth3 authentication
   - 🐛 fix(api): handle null response from server
   - 📚 docs(readme): update installation instructions
   - 💅 style(ui): format button component
   - ♻️ refactor(db): optimize database queries
   - ✅ test(api): add unit tests for user endpoints
   - 🔧 chore(deps): update dependencies

Write ONLY the commit message in the conventional format. Do not include any explanatory text, file paths, or other content."""

        user_prompt = f"""Write a conventional commit message for these changes:

{diff}

Focus on:
2. What type of change this is (feat, fix, etc.)
3. What part of the codebase is affected (scope)
4. What the change accomplishes (description)
5. If multiple files are changed, identify the common theme or purpose

Write ONLY the commit message in the conventional format. Do not include any explanatory text."""

        message = self.generate_completion(
            system_prompt, user_prompt, temperature=temperature
        )

        # Clean up the response to ensure it's a valid commit message
        lines = [line.strip() for line in message.split("\n") if line.strip()]

        # Find the first line that looks like a commit message
        for line in lines:
            # Skip lines that are explanations or contain file paths
            if any(
                skip in line.lower()
                for skip in [
                    "based on",
                    "changes in",
                    "can be written",
                    "commit message",
                    "following",
                    "these changes",
                    "the changes",
                ]
            ):
                continue

            # Skip lines that are just file paths
            if line.startswith("`") or line.startswith("/") or ":" in line:
                continue

            message = line
            break
        else:
            # If no valid message found, use the first non-empty line
            message = lines[0] if lines else "chore: update code"

        # Remove any pull request references from the main message
        message = (
            message.split("(")[1].strip()
            if "(" in message and "#" in message
            else message
        )

        # Ensure the message starts with an emoji
        if not any(
            emoji in message for emoji in ["✨", "🐛", "📚", "💅", "♻️", "✅", "🔧"]
        ):
            # Add appropriate emoji based on the commit type
            if message.startswith("feat"):
                message = "✨ " + message
            elif message.startswith("fix"):
                message = "🐛 " + message
            elif message.startswith("docs"):
                message = "📚 " + message
            elif message.startswith("style"):
                message = "💅 " + message
            elif message.startswith("refactor"):
                message = "♻️ " + message
            elif message.startswith("test"):
                message = "✅ " + message
            elif message.startswith("chore"):
                message = "🔧 " + message
            else:
                message = "🔧 " + message  # Default to chore

        return message

    def generate_batch_messages(
        self, diffs: Dict[str, str], temperature: Optional[float] = None
    ) -> Dict[str, str]:
        """Generate commit messages for multiple files.

        Args:
            diffs: Dictionary mapping file paths to their diffs
            temperature: Optional temperature for AI generation

        Returns:
            Dictionary mapping file paths to their commit messages
        """
        # If only one file, use the single file method
        if len(diffs) == 1:
            file_path, diff = next(iter(diffs.items()))
            return {file_path: self.generate_commit_message(diff, temperature)}

        # Combine all diffs with clear file separators
        combined_diff = "\n\n".join(
            f"Changes in {file_path}:\n{diff}" for file_path, diff in diffs.items()
        )

        # Generate a single commit message for all changes
        message = self.generate_commit_message(combined_diff, temperature)

        # Return the same message for all files
        return {file_path: message for file_path in diffs.keys()}

    def generate_changelog(
        self, commits: List[str], version: str, temperature: Optional[float] = None
    ) -> str:
        """Generate a changelog from a list of commits."""
        system_prompt = """You are a helpful AI that generates changelogs.
        Follow these rules:
        2. Group changes by type (Added, Changed, Fixed, etc.)
        3. Keep descriptions concise but informative
        4. Use past tense
        5. Start each entry with a verb"""

        user_prompt = (
            f"Generate a changelog for version {version} with these commits:\n\n"
            + "\n".join(commits)
        )

        return self.generate_completion(
            system_prompt, user_prompt, temperature=temperature
        )
