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

1. Format: type(scope): description
   - type: One of feat, fix, docs, style, refactor, test, chore
   - scope: Optional, describes the section of the codebase affected
   - description: Clear, concise explanation of the change

2. Types and their emojis:
   - feat: ✨ (new feature or enhancement)
   - fix: 🐛 (bug fix)
   - docs: 📚 (documentation changes)
   - style: 💅 (formatting, missing semi colons, etc; no code change)
   - refactor: ♻️ (code restructuring, no functional changes)
   - test: ✅ (adding or modifying tests)
   - chore: 🔧 (maintenance tasks, dependencies, etc)

3. Guidelines:
   - Keep the description under 72 characters
   - Use imperative mood ("add" not "added")
   - Don't end with a period
   - Focus on the "why" not the "what"
   - Be specific about the change
   - Use present tense
   - Start with a verb

4. Examples:
   - ✨ feat(auth): add OAuth2 authentication
   - 🐛 fix(api): handle null response from server
   - 📚 docs(readme): update installation instructions
   - 💅 style(ui): format button component
   - ♻️ refactor(db): optimize database queries
   - ✅ test(api): add unit tests for user endpoints
   - 🔧 chore(deps): update dependencies

Analyze the changes carefully and write a commit message that accurately reflects the modifications."""

        user_prompt = f"""Analyze these changes and write a conventional commit message:

{diff}

Focus on:
1. What type of change this is (feat, fix, etc.)
2. What part of the codebase is affected (scope)
3. What the change accomplishes (description)

Write a single-line commit message following the conventional format."""

        message = self.generate_completion(
            system_prompt, user_prompt, temperature=temperature
        )

        # Clean up the response to ensure it's a valid commit message
        message = message.split("\n")[0].strip()

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

    def generate_changelog(
        self, commits: List[str], version: str, temperature: Optional[float] = None
    ) -> str:
        """Generate a changelog from a list of commits."""
        system_prompt = """You are a helpful AI that generates changelogs.
        Follow these rules:
        1. Group changes by type (Added, Changed, Fixed, etc.)
        2. Keep descriptions concise but informative
        3. Use past tense
        4. Start each entry with a verb"""

        user_prompt = (
            f"Generate a changelog for version {version} with these commits:\n\n"
            + "\n".join(commits)
        )

        return self.generate_completion(
            system_prompt, user_prompt, temperature=temperature
        )
