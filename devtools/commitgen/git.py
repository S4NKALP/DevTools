"""
Git service for commit_gen tool.
"""

from typing import List, Optional
from ..shared.git import GitService
from ..shared.config import Config
import os


class CommitGenGitService(GitService):
    """Git service for commit_gen tool."""

    def __init__(self, config: Config):
        """Initialize commit_gen git service."""
        super().__init__(os.getcwd())  # Use current directory as repo path
        self.config = config

    def get_staged_changes(self, files: Optional[List[str]] = None) -> str:
        """Get staged changes as a diff.

        Args:
            files: Optional list of files to get changes for
        """
        diffs = self.get_all_diffs(staged=True)
        if files:
            diffs = {file: diff for file, diff in diffs.items() if file in files}
        return "\n\n".join(
            f"Changes in {file}:\n{diff}" for file, diff in diffs.items()
        )

    def get_staged_changes_map(
        self, files: Optional[List[str]] = None
    ) -> dict[str, str]:
        """Get staged changes as a mapping of file -> diff.

        Args:
            files: Optional list of files to get changes for

        Returns:
            Dict mapping file path to its staged diff
        """
        diffs = self.get_all_diffs(staged=True)
        if files:
            diffs = {file: diff for file, diff in diffs.items() if file in files}
        return diffs

    def get_unstaged_changes(self) -> str:
        """Get unstaged changes as a diff."""
        diffs = self.get_all_diffs(staged=False)
        return "\n\n".join(
            f"Changes in {file}:\n{diff}" for file, diff in diffs.items()
        )

    def commit_changes(self, message: str, sign: bool = False) -> None:
        """Commit changes with the given message."""
        ok, stdout, stderr, code = self.commit_verbose(message, sign=sign)
        if not ok:
            details = stderr or stdout or f"exit code {code}"
            raise Exception(f"Failed to commit changes: {details}")

    def push_changes(self) -> None:
        """Push changes to the current branch."""
        if not self.push():
            raise Exception("Failed to push changes")

    def get_recent_commits(self, limit: int = 10) -> List[str]:
        """Get recent commit messages."""
        commits = self.get_commit_history(limit=limit)
        return [commit["message"] for commit in commits]
