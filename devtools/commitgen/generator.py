"""
Commit message and changelog generation using AI.
"""

from typing import Dict, List, Optional

from ..shared.ai import AIService
from ..shared.config import Config


class CommitGenerator(AIService):
    """AI-powered commit message and changelog generator."""

    def __init__(self, config: Config):
        """Initialize commit generator."""
        super().__init__(config)
        # Read emoji preference from config (default: disabled)
        self.use_emoji: bool = bool(
            str(self.config.get("emoji", "false")).strip().lower()
            in [
                "1",
                "true",
                "yes",
                "on",
            ]
        )

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
Output ONLY the commit message in the correct format{" with emoji" if self.use_emoji else " without any emoji"}."""

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

        # Apply or remove emoji based on configuration (strict removal when disabled)
        if self.use_emoji:
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
                    message = "🔧 " + message
        else:
            # Remove any known emojis anywhere in the message
            for emoji in ["✨", "🐛", "📚", "💅", "♻️", "✅", "🔧"]:
                message = message.replace(emoji, "")
            message = " ".join(message.split())

        return message

    def _parse_analysis_result(self, analysis: str) -> bool:
        """Parse and validate the analysis result from AI.

        Args:
            analysis: Raw analysis output from AI

        Returns:
            bool: True if changes should be grouped, False otherwise

        Raises:
            ValueError: If analysis result cannot be reliably determined
        """
        # Normalize the analysis text
        analysis = analysis.strip().upper()

        # Direct matches
        if "GROUP" in analysis and "SEPARATE" not in analysis:
            return True
        if "SEPARATE" in analysis and "GROUP" not in analysis:
            return False

        # Check for strong indicators in the explanation
        group_indicators = [
            "RELATED",
            "SAME FEATURE",
            "SAME FIX",
            "SAME SCOPE",
            "SAME PURPOSE",
            "SHOULD BE GROUPED",
            "COMBINED",
        ]
        separate_indicators = [
            "UNRELATED",
            "DIFFERENT",
            "SEPARATE",
            "INDEPENDENT",
            "SHOULD BE SEPARATE",
            "DISTINCT",
        ]

        # Count indicators
        group_count = sum(1 for ind in group_indicators if ind in analysis)
        separate_count = sum(1 for ind in separate_indicators if ind in analysis)

        # If we have a clear majority, use that
        if group_count > separate_count and group_count > 0:
            return True
        if separate_count > group_count and separate_count > 0:
            return False

        # If we can't determine reliably, raise an error
        raise ValueError(
            f"Could not reliably determine grouping from analysis: {analysis}"
        )

    def _validate_commit_message(self, message: str) -> str:
        """Validate and clean up a generated commit message.

        Args:
            message: Raw commit message from AI

        Returns:
            str: Cleaned and validated commit message
        """
        # Remove any markdown code blocks
        message = message.replace("```", "").strip()

        # Remove any explanatory text
        lines = [line.strip() for line in message.split("\n") if line.strip()]
        for line in lines:
            # Skip lines that look like explanations
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
                    "here's",
                    "this is",
                ]
            ):
                continue
            # Skip lines that look like code or commands
            if line.startswith("`") or line.startswith("/") or ":" in line:
                continue
            message = line
            break
        else:
            message = lines[0] if lines else "🔧 chore: update code"

        # Ensure proper emoji prefix or strip strictly according to config
        if self.use_emoji:
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
                    message = "🔧 " + message
        else:
            for emoji in ["✨", "🐛", "📚", "💅", "♻️", "✅", "🔧"]:
                message = message.replace(emoji, "")
            message = " ".join(message.split())

        return message

    def generate_batch_messages(
        self, diffs: Dict[str, str], temperature: Optional[float] = None
    ) -> Dict[str, str]:
        """Generate commit messages for multiple files with intelligent grouping.

        This method analyzes the diffs to determine if they should be grouped into a single
        commit message or kept separate based on their relationship and scope.

        Args:
            diffs: Dictionary mapping file paths to their diffs
            temperature: Optional temperature for generation

        Returns:
            Dictionary mapping file paths to their commit messages
        """
        if not diffs:
            return {}

        if len(diffs) == 1:
            file_path, diff = next(iter(diffs.items()))
            message = self.generate_commit_message(diff, temperature)
            return {file_path: self._validate_commit_message(message)}

        # First, analyze the diffs to determine if they should be grouped
        system_prompt = """You are an expert at analyzing code changes and determining their relationships.
Analyze the provided diffs and determine if they represent related changes that should be grouped together.
Consider:
1. Are the changes part of the same feature or fix?
2. Do they share a common scope or purpose?
3. Would separating them make the commit history less meaningful?

Respond with either:
- "GROUP" if the changes should be combined into one commit
- "SEPARATE" if the changes should have individual commit messages
Include a brief explanation of your reasoning."""

        # Prepare the diffs for analysis
        analysis_input = "\n\n".join(
            f"File: {file_path}\nChanges:\n{diff}" for file_path, diff in diffs.items()
        )

        try:
            analysis = self.generate_completion(
                system_prompt,
                f"Analyze these changes:\n\n{analysis_input}",
                temperature=0.1,  # Lower temperature for more consistent analysis
            )
            should_group = self._parse_analysis_result(analysis)
        except Exception as e:
            print(
                f"Warning: Failed to analyze changes, defaulting to separate messages: {
                    e
                }"
            )
            should_group = False

        if should_group:
            # Generate a single commit message for all changes
            try:
                # Create a structured diff that maintains file context
                structured_diff = "\n\n".join(
                    f"=== Changes in {file_path} ===\n{diff}"
                    for file_path, diff in diffs.items()
                )

                message = self.generate_commit_message(structured_diff, temperature)
                message = self._validate_commit_message(message)
                return {file_path: message for file_path in diffs.keys()}
            except Exception as e:
                # Fallback to individual messages if combined generation fails
                print(f"Warning: Failed to generate combined message: {e}")
                should_group = False

        if not should_group:
            # Generate individual messages for each file in parallel
            import time
            from concurrent.futures import ThreadPoolExecutor
            from queue import Queue
            from threading import Lock

            # Rate limiting setup
            RATE_LIMIT = 5  # requests per second
            rate_limit_queue = Queue()
            rate_limit_lock = Lock()
            last_request_time = time.time()

            def rate_limited_generate(file_path: str, diff: str) -> tuple[str, str]:
                """Generate commit message with rate limiting."""
                nonlocal last_request_time

                with rate_limit_lock:
                    # Calculate time to wait
                    current_time = time.time()
                    time_since_last = current_time - last_request_time
                    if time_since_last < 1.0 / RATE_LIMIT:
                        time.sleep(1.0 / RATE_LIMIT - time_since_last)

                    try:
                        message = self.generate_commit_message(diff, temperature)
                        message = self._validate_commit_message(message)
                        last_request_time = time.time()
                        return file_path, message
                    except Exception as e:
                        print(
                            f"Warning: Failed to generate message for {file_path}: {e}"
                        )
                        return file_path, "🔧 chore: update code"

            # Use ThreadPoolExecutor with a reasonable number of workers
            max_workers = min(len(diffs), 10)  # Cap at 10 concurrent workers
            results = {}

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_file = {
                    executor.submit(rate_limited_generate, file_path, diff): file_path
                    for file_path, diff in diffs.items()
                }

                # Collect results as they complete
                for future in future_to_file:
                    try:
                        file_path, message = future.result()
                        results[file_path] = message
                    except Exception as e:
                        file_path = future_to_file[future]
                        print(f"Warning: Failed to process {file_path}: {e}")
                        results[file_path] = "🔧 chore: update code"

            return results

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
