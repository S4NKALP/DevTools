# Changelog

## v0.1.1

✨ Added
- ✨ Added pyproject.toml for PEP 517/518 build support.
- ✨ Added `--no-verify` option to bypass git hooks during commit.
- ✨ Added per-file commit generation option.
- ✨ Added git hooks management and auto-fix on pre-commit.
- ✨ Added git hooks management CLI.
- ✨ Added emoji option to CLI and config to control emoji prefixes.

🔄 Changed
- 🔄 Replaced ruff linter with black.

🐛 Fixed
- 🐛 Removed duplicate changelog entries.

🚀 Performance

📝 Documentation
- 📝 Added initial todo list for project improvements.
- 📝 Updated README with new features, aliases, and configuration details.
- 📝 Recommended installation using pipx and uv.

🔧 Maintenance
- 🔧 Improved installation instructions and package metadata for PyPI release.

 Refactor
- 🔄 Improved emoji handling and sanitization in commit message generation.
- 🔄 Improved changelog generation and sanitization of AI output.
- 🔄 Improved changelog generation to handle existing files and duplicate headers.

## v0.1.0

✨ Added
- Updated changelog format and added ChangelogGenerator class documentation 📚
- Updated `README.md` file with the new commit message format and ChangelogGenerator class usage 📝
- ✨ docs(changelog): Add ChangelogGenerator class documentation
- 🐛 docs(changelog): Updated changelog format and added ChangelogGenerator class documentation

🔄 Changed
- Changes for version 0.1.0:
- Updated commit message and changelog generation using AI 👨‍💻
- Updated `GitService` to return exit code from `_run_git_command` and improved `get_commit_history` method signature and docstring 📝
- Updated changelog format for clarity and consistency 📚
- Updated `LICENSE` 📄
- 🔄 refactor(generator): Update commit message and changelog generation using AI
- 🔄 refactor(devtools/shared/git.py): Update GitService to return exit code from `_run_git_command` and improve `get_commit_history` method signature and docstring
- 🔄 docs(changelog): Updated changelog format for clarity and consistency
- 📚 Update `README.md` file
- 📚 Update `LICENSE`

🗑️ Removed
- Removed unused variable in `_run_git_command` calls 🗑️