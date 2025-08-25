# Changelog

## v0.1.1

✨ Added
- Added git hooks management and auto-fix on pre-commit
- Added git hooks management CLI
- Added emoji option to cli and config to control emoji prefixes

🔄 Changed
- Improved changelog generation to handle existing files and duplicate headers

🗑️ Removed
- Removed duplicate changelog entries

📝 Documentation
- Updated changelog for v0.1.1 release
- Recommended installation using pipx and uv

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