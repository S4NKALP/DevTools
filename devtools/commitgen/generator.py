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
        system_prompt = """You are an expert Git assistant trained to write highly effective and conventional commit messages.

Your task is to analyze the provided code diff and generate a commit message in the following format:

Format: type(scope): description
- type: One of feat, fix, docs, style, refactor, test, chore
- scope: Optional but encouraged; represents the part of the codebase affected (e.g. auth, api, db, ui)
- description: A short, clear explanation of the change

Each type has an emoji prefix:
- ✨ feat: New feature
- 🐛 fix: Bug fix
- 📚 docs: Documentation-only change
- 💅 style: Code formatting (no logic change)
- ♻️ refactor: Code changes without affecting behavior
- ✅ test: Test additions/changes
- 🔧 chore: Maintenance, build, or config tasks

Strict rules:
- Write the entire message in a single line
- Use imperative mood (e.g. "add" not "added")
- No file paths, no periods at the end
- Avoid generic or vague descriptions
- Don't mention pull requests, issues, or reviewers
- Focus on the why and impact of the change, not just the what

Examples:
- ✨ feat(auth): add OAuth2 login support
- 🐛 fix(api): return correct HTTP status for invalid input
- ♻️ refactor(db): simplify user query joins

Output ONLY the commit message. Do not include any comments or explanations."""

        user_prompt = f"""Generate a single-line conventional commit message for the following code changes:

{diff}

Identify the most relevant type, a concise scope, and the purpose of the change.
Output ONLY the commit message in the correct format (with emoji)."""

        message = self.generate_completion(
            system_prompt, user_prompt, temperature=temperature
        )

        lines = [line.strip() for line in message.split("\n") if line.strip()]

        for line in lines:
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
            if line.startswith("`") or line.startswith("/") or ":" in line:
                continue
            message = line
            break
        else:
            message = lines[0] if lines else "🔧 chore: update code"

        if not any(
            emoji in message for emoji in ["✨", "🐛", "📚", "💅", "♻️", "✅", "🔧"]
        ):
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
                message = "🔧 " + message  # fallback

        return message

    def generate_batch_messages(
        self, diffs: Dict[str, str], temperature: Optional[float] = None
    ) -> Dict[str, str]:
        """Generate commit messages for multiple files."""
        if len(diffs) == 1:
            file_path, diff = next(iter(diffs.items()))
            return {file_path: self.generate_commit_message(diff, temperature)}

        combined_diff = "\n\n".join(
            f"Changes in {file_path}:\n{diff}" for file_path, diff in diffs.items()
        )

        message = self.generate_commit_message(combined_diff, temperature)

        return {file_path: message for file_path in diffs.keys()}

    def generate_changelog(
        self, commits: List[str], version: str, temperature: Optional[float] = None
    ) -> str:
        """Generate a changelog from a list of commits."""
        system_prompt = """You are a professional release manager generating changelogs from commit messages.

Follow these rules:
- Group entries under clear sections: Added, Changed, Fixed, Removed, Refactored, Tests, Chore, etc.
- Use past tense (e.g. "Added login flow", not "Add login flow")
- Write concise but informative summaries
- Each bullet point should start with a verb (e.g. "Fixed", "Added")
- Skip commit types like "chore" unless they are user-relevant
- Format sections like this:

## [version]
### Added
- Added support for OAuth2 authentication

### Fixed
- Fixed issue where empty input crashed the API

Do NOT include raw commit messages. Use the commit messages as input and convert them into user-facing changelog entries."""

        user_prompt = (
            f"Generate a clean and structured changelog for version {
                version
            } using these commits:\n\n"
            + "\n".join(commits)
        )

        return self.generate_completion(
            system_prompt, user_prompt, temperature=temperature
        )
