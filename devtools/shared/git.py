"""
Shared Git service for devtools.
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import os
from datetime import datetime, timedelta


class GitService:
    """Base Git service that can be extended by specific tools."""

    def __init__(self, repo_path: str):
        """Initialize GitService with repository path."""
        self.repo_path = repo_path
        if not os.path.exists(os.path.join(repo_path, ".git")):
            raise ValueError(f"Not a git repository: {repo_path}")

    def _is_git_repo(self) -> bool:
        """Check if the current directory is a git repository."""
        try:
            subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def _run_git_command(self, args: List[str]) -> Tuple[str, str, int]:
        """Run a git command and return its output and return code."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except subprocess.CalledProcessError as e:
            return e.stdout.strip(), e.stderr.strip(), e.returncode

    def get_staged_files(self) -> List[str]:
        """Get list of staged files."""
        stdout, _, _ = self._run_git_command(["diff", "--cached", "--name-only"])
        return stdout.splitlines() if stdout else []

    def get_unstaged_files(self) -> List[str]:
        """Get list of unstaged files."""
        stdout, _, _ = self._run_git_command(
            ["ls-files", "--modified", "--others", "--exclude-standard"]
        )
        return stdout.splitlines() if stdout else []

    def get_diff(self, file_path: str, staged: bool = True) -> str:
        """Get diff for a specific file."""
        args = ["diff", "--cached" if staged else ""]
        if file_path:
            args.append(file_path)
        stdout, _, _ = self._run_git_command(args)
        return stdout

    def get_all_diffs(self, staged: bool = True) -> Dict[str, str]:
        """Get diffs for all changed files."""
        files = self.get_staged_files() if staged else self.get_unstaged_files()
        return {file: self.get_diff(file, staged) for file in files}

    def commit(self, message: str, sign: bool = False, no_verify: bool = False) -> bool:
        """Create a commit with the given message."""
        args = ["commit"]
        if sign:
            args.append("-S")
        if no_verify:
            args.append("--no-verify")
        args.extend(["-m", message])
        stdout, stderr, returncode = self._run_git_command(args)
        return returncode == 0

    def commit_verbose(
        self, message: str, sign: bool = False, no_verify: bool = False
    ) -> Tuple[bool, str, str, int]:
        """Create a commit and return success and raw outputs.

        Returns:
            (ok, stdout, stderr, returncode)
        """
        args = ["commit"]
        if sign:
            args.append("-S")
        if no_verify:
            args.append("--no-verify")
        args.extend(["-m", message])
        stdout, stderr, returncode = self._run_git_command(args)
        return returncode == 0, stdout, stderr, returncode

    def commit_paths_verbose(
        self,
        message: str,
        files: List[str],
        sign: bool = False,
        no_verify: bool = False,
    ) -> Tuple[bool, str, str, int]:
        """Create a commit including only the specified files.

        Returns:
            (ok, stdout, stderr, returncode)
        """
        if not files:
            return False, "", "no files specified", 1
        args = ["commit"]
        if sign:
            args.append("-S")
        if no_verify:
            args.append("--no-verify")
        args.extend(["-m", message, "--"] + list(files))
        stdout, stderr, returncode = self._run_git_command(args)
        return returncode == 0, stdout, stderr, returncode

    def commit_paths_verbose(
        self, message: str, files: List[str], sign: bool = False
    ) -> Tuple[bool, str, str, int]:
        """Create a commit including only the specified files.

        Returns:
            (ok, stdout, stderr, returncode)
        """
        if not files:
            return False, "", "no files specified", 1
        args = ["commit"]
        if sign:
            args.append("-S")
        args.extend(["-m", message, "--"] + list(files))
        stdout, stderr, returncode = self._run_git_command(args)
        return returncode == 0, stdout, stderr, returncode

    def get_repo_name(self) -> str:
        """Get the repository name."""
        stdout, _, _ = self._run_git_command(["rev-parse", "--show-toplevel"])
        return Path(stdout).name

    def get_current_branch(self) -> str:
        """Get the current branch name."""
        stdout, _, _ = self._run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
        return stdout

    def push(self, branch: Optional[str] = None) -> bool:
        """Push changes to remote."""
        if not branch:
            branch = self.get_current_branch()
        stdout, stderr, returncode = self._run_git_command(["push", "origin", branch])
        return returncode == 0

    def get_staged_changes(self, files: Optional[List[str]] = None) -> Dict[str, str]:
        """Get staged changes for specified files or all staged changes."""
        try:
            diffs = {}  # Initialize diffs at the start

            if files:
                for file in files:
                    result = subprocess.run(
                        ["git", "diff", "--staged", "--", file],
                        cwd=self.repo_path,
                        capture_output=True,
                        text=True,
                    )
                    if result.stdout:
                        diffs[file] = result.stdout
            else:
                result = subprocess.run(
                    ["git", "diff", "--staged"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                )
                if result.stdout:
                    # Parse the diff to get individual file changes
                    current_file = None
                    current_diff = []

                    for line in result.stdout.split("\n"):
                        if line.startswith("diff --git"):
                            if current_file and current_diff:
                                diffs[current_file] = "\n".join(current_diff)
                            current_file = line.split("b/")[-1].strip()
                            current_diff = [line]
                        elif current_file:
                            current_diff.append(line)

                    if current_file and current_diff:
                        diffs[current_file] = "\n".join(current_diff)

            return diffs
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get staged changes: {str(e)}")

    def stage_all_changes(self) -> None:
        """Stage all changes in the repository."""
        try:
            subprocess.run(["git", "add", "."], cwd=self.repo_path, check=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to stage changes: {str(e)}")

    def get_commit_history(
        self, since: Optional[str] = None, limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """Get commit history.

        Args:
            since: Get commits since this reference (tag, commit, etc.)
            limit: Maximum number of commits to return
        """
        args = [
            "log",
            "--pretty=format:%H%n%an%n%ad%n%B%n==END==",
            "--date=format:%Y-%m-%d %H:%M:%S %z",
        ]

        if since:
            args.append(f"{since}..HEAD")
        if limit:
            args.append(f"-n {limit}")

        stdout, _, _ = self._run_git_command(args)

        commits = []
        current_commit = []

        for line in stdout.split("\n"):
            if line == "==END==":
                if current_commit:
                    commit_hash, author, date, *message_lines = current_commit
                    commits.append(
                        {
                            "hash": commit_hash,
                            "author": author,
                            "date": date,
                            "message": "\n".join(message_lines),
                        }
                    )
                current_commit = []
            else:
                current_commit.append(line)

        return commits

    def get_commits_since_tag(self, tag: str) -> List[Dict[str, str]]:
        """Get commits since a tag.

        Args:
            tag: Git tag to use as reference point

        Returns:
            List of commit dictionaries with hash and message
        """
        cmd = ["git", "log", f"{tag}..HEAD", "--pretty=format:%H|%s"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)
        result.check_returncode()

        commits = []
        for line in result.stdout.splitlines():
            hash_, message = line.split("|", 1)
            commits.append({"hash": hash_, "message": message})

        return commits

    def get_commits_since_date(self, days: int) -> List[Dict[str, str]]:
        """Get commits since a date.

        Args:
            days: Number of days to look back

        Returns:
            List of commit dictionaries with hash and message
        """
        # Calculate date
        date = datetime.now() - timedelta(days=days)
        date_str = date.strftime("%Y-%m-%d")

        # Get commits
        cmd = ["git", "log", f"--since={date_str}", "--pretty=format:%H|%s"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)
        result.check_returncode()

        commits = []
        for line in result.stdout.splitlines():
            hash_, message = line.split("|", 1)
            commits.append({"hash": hash_, "message": message})

        return commits
