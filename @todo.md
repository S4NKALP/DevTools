## DevTools – Project Improvements (@todo)

### Product & Features
- [ ] Add `devtools repo init` wizard to bootstrap new repos (license, gitignore, README).
- [ ] Support custom commit templates and per-repo rules.
- [ ] Add `devtools commit guard` pre-commit hook generator.
- [ ] Offline mode for commit suggestions.
- [ ] Changelog: support Keep a Changelog format and semver sections.
- [ ] Gitignore: local cache of templates and fallback when API is down.
- [ ] License: add SPDX ID validation and dual-licensing templates.

### AI Providers & Config
- [ ] Provider auto-detection and graceful fallback chain.
- [ ] Add Local (Ollama) providers.
- [ ] Config schema validation with helpful error messages.
- [ ] `devtools config import/export` for sharing presets.

### CLI UX
- [ ] Global `--verbose/--quiet` and `--no-color` flags.
- [ ] Rich TUI progress spinners and structured error output.
- [ ] Interactive prompts with safe defaults and confirmation steps.
- [ ] Shell completion (bash/zsh/fish) generation command.

### Packaging & Distribution
- [x] Publish to PyPI
- [x] Provide `uv`/`pipx` installation guide.
- [x] Add `pyproject.toml` and PEP 517/518 build backend.
- [ ] Arch AUR PKGBUILD (devtools-bin and devtools-git).

### Quality: Testing & Linting
- [ ] Unit tests for each subcommand (commit, changelog, gitignore, license).
- [ ] Golden-file tests for changelog output.
- [ ] Contract tests for provider integrations with fixtures/mocks.
- [ ] Add type hints and enable mypy in strict mode where feasible.
- [ ] Configure ruff ruleset and pre-commit hooks.







