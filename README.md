# DevTools

A collection of developer tools to enhance your workflow. This package includes tools for generating commit messages, changelogs, and .gitignore files, all accessible from a single unified CLI: `devtools`.

## Installation

```bash
# Clone the repository
$ git clone https://github.com/S4NKALP/DevTools.git
$ cd devtools

# Install in editable mode
$ pip install -e .
```

## Configuration

### API Keys

The tools use various APIs that require API keys. You can set these using the config command:

```bash
# Set OpenRouter API key (for AI features)
devtools config set OPENROUTER_API_KEY "your-openrouter-api-key"

# Set GitHub API key (optional, for enhanced features)
devtools config set github_api_key "your-github-api-key"
```

Or set them in your environment:

```bash
# OpenRouter API key
export OPENROUTER_API_KEY="your-openrouter-api-key"

# GitHub API key
export GITHUB_API_KEY="your-github-api-key"
```

Or create a `.env` file in your project root:

```bash
OPENROUTER_API_KEY=your-openrouter-api-key
GITHUB_API_KEY=your-github-api-key
```

### Managing Configuration

```bash
# Show all configuration
devtools config show

# Show specific value
devtools config show OPENROUTER_API_KEY

# Delete a value
devtools config delete OPENROUTER_API_KEY

# Clear all configuration
devtools config clear
```

Configuration files are stored in:

- `~/.devtools/config.yaml`

Example config.yaml:

```yaml
# API Keys
OPENROUTER_API_KEY:

# AI Settings
max_tokens: 1024
temperature: 0.7
output_format: text

# Commit Settings
conventional_commits: true

# Repository Settings
repositories: []
```

## Usage

All tools are available under the main `devtools` command:

```
devtools [COMMAND] [SUBCOMMAND] [OPTIONS]
```

### Commit Message Generator

Generate and apply commit messages, create changelogs, and manage configuration.

#### Generate Commit Message

```bash
devtools commit generate [OPTIONS]
```

**Options:**

- `--files, -f [FILE]...` Specific files to generate commit messages for
- `--repo, -r PATH` Repository path (default: current directory)
- `--commit, -c` Automatically commit changes
- `--push, -p` Push changes after commit
- `--conventional/--no-conventional` Use conventional commit format (default: True)
- `--no-stage` Skip automatic staging of changes
- `--sign` Sign commits with GPG
- `--temperature FLOAT` AI temperature (0.0-1.0)

Commit messages follow the conventional format with emojis:

- ✨ feat: New feature
- 🐛 fix: Bug fix
- 📚 docs: Documentation
- 💅 style: Formatting, missing semi colons, etc
- ♻️ refactor: Code refactoring
- ✅ test: Adding tests
- 🔧 chore: Maintenance

#### Changelog Generation

```bash
# Generate from git history
devtools commit changelog generate [OPTIONS]

# Generate interactively
devtools changelog generate [OPTIONS]

# Generate from a file
devtools changelog generate-from-file [OPTIONS]
```

**Options:**

- `--version, -v VERSION` Version number for the changelog entry (required)
- `--from-tag, -t TAG` Generate changelog from this tag
- `--days, -d N` Generate changelog from the last N days
- `--commits, -n N` Generate changelog from the last N commits
- `--output, -o FILE` Output file path (default: CHANGELOG.md)
- `--temperature FLOAT` AI temperature (0.0-1.0)
- `--input, -i FILE` Input file with changes (for file-based generation)

The changelog generator supports three modes:

1. Git history: Automatically generates changelog from commit history
2. Interactive: Enter changes manually with emoji prefixes
3. File-based: Generate from a file containing changes

Changes are grouped by type with emojis:

- ✨ Added
- 🔄 Changed
- 🐛 Fixed
- 🚀 Performance
- 📝 Documentation
- 🔧 Maintenance
- 🗑️ Removed
- 🔒 Security

#### Repository Status

```bash
devtools commit status
```

---

### Gitignore Generator

Generate .gitignore files for your project, either by auto-detecting project types or specifying technologies.

#### Auto-detect Project Types

```bash
devtools gitignore auto [OPTIONS]
```

**Options:**

- `--directory, -d DIR` Directory to scan (default: current directory)
- `--output, -o FILE` Output file path (default: .gitignore)

#### Generate for Specific Technologies

```bash
devtools gitignore generate python django vscode [OPTIONS]
```

**Options:**

- `--output, -o FILE` Output file path (default: .gitignore)

The generator uses the gitignore.io API to fetch templates. No API key is required.

---

## Features

- **Commit Message Generator:**
  - AI-powered commit message suggestions using Mixtral 8x7B
  - Conventional commit format with emojis
  - GPG signing and push support
  - Changelog generation from commit history
  - Repository status with diff previews
- **Gitignore Generator:**
  - Auto-detects project types and generates .gitignore
  - Uses gitignore.io API for up-to-date templates
  - No API key required
  - Falls back to generic template if API is unavailable

## Requirements

- Python 3.8+
- Git
- OpenRouter API key (for AI features)
- GitHub API key (optional)

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Lint
ruff .
```

## Contributing

Contributions are welcome! Please open issues or submit pull requests.

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0) - see the LICENSE file for details.
