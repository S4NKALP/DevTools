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
        system_prompt = """You are an expert Git assistant trained to write clean, conventional commit messages with optional bodies.

Follow this format:

<type>(<scope>): <short summary>
[blank line]
<detailed body explaining the change>

Where:
- type: One of feat, fix, docs, style, refactor, test, chore
- scope: Optional but recommended (e.g. auth, api, db)
- summary: A short, one-line description of the change
- body: (Optional) Add context, rationale, and details about the change

Each type must have an emoji:
- ✨ feat: New feature
- 🐛 fix: Bug fix
- 📚 docs: Documentation
- 💅 style: Formatting (no code logic)
- ♻️ refactor: Code restructure without behavior change
- ✅ test: Tests added or modified
- 🔧 chore: Maintenance, configs, build scripts, etc.

Rules:
- Subject must be a single line, max ~72 characters
- Use imperative mood: “add”, not “added”
- Don’t include file paths, issue numbers, or PR references
- Use body only if extra context is helpful (start with a verb or full sentence)
- Don’t include explanations about what can be written
- DO NOT include “commit message” or meta-language

Examples:
✨ feat(auth): add OAuth2 login support

Adds full OAuth2 login flow using access and refresh tokens.
This improves external authentication and reduces local user management.
"""

        user_prompt = f"""Generate a conventional commit message for the following code changes:

{diff}

- Include a single-line subject
- Add a body section if useful, separated by a blank line
- Output must match the conventional commit format
- Use the correct emoji prefix
"""

        message = self.generate_completion(
            system_prompt, user_prompt, temperature=temperature
        )

        # Clean and extract subject and optional body
        lines = [line.rstrip() for line in message.splitlines()]
        subject = ""
        body_lines = []

        for i, line in enumerate(lines):
            if not subject and line and ":" in line:
                subject = line.strip()
                continue
            if subject:
                body_lines = lines[i:]
                break

        if not subject:
            subject = "🔧 chore: update code"

        # Ensure emoji in the subject
        if not any(
            emoji in subject for emoji in ["✨", "🐛", "📚", "💅", "♻️", "✅", "🔧"]
        ):
            if subject.startswith("feat"):
                subject = "✨ " + subject
            elif subject.startswith("fix"):
                subject = "🐛 " + subject
            elif subject.startswith("docs"):
                subject = "📚 " + subject
            elif subject.startswith("style"):
                subject = "💅 " + subject
            elif subject.startswith("refactor"):
                subject = "♻️ " + subject
            elif subject.startswith("test"):
                subject = "✅ " + subject
            elif subject.startswith("chore"):
                subject = "🔧 " + subject
            else:
                subject = "🔧 " + subject

        # Final formatted message
        message = subject
        if body_lines:
            body = "\n".join(line.strip() for line in body_lines if line.strip())
            if body:
                message += "\n\n" + body

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
- Group changes by type (Added, Changed, Fixed, etc.)
- Keep descriptions concise but informative
- Use past tense
- Start each entry with a verb
"""

        user_prompt = (
            f"Generate a changelog for version {version} with these commits:\n\n"
            + "\n".join(commits)
        )

        return self.generate_completion(
            system_prompt, user_prompt, temperature=temperature
        )
