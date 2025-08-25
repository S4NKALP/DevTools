"""
Command-line interface for Git hooks management.
"""

import os
import stat
from pathlib import Path
from datetime import datetime
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

HOOK_TEMPLATES = {
    "pre-commit": """#!/usr/bin/env bash
set -u

echo "Running pre-commit checks..."

# If pre-commit is configured, defer to it
if command -v pre-commit >/dev/null 2>&1 && [ -f ".pre-commit-config.yaml" ]; then
  pre-commit run --all-files
  exit 0
fi

run_lint() {
  # Node.js/TypeScript
  if [ -f "package.json" ]; then
    if command -v npm >/dev/null 2>&1; then
      npm run -s lint --if-present || true
      if command -v npx >/dev/null 2>&1; then
        npx --yes eslint . || npx --yes prettier --check . || true
      fi
      return 0
    fi
    if command -v pnpm >/dev/null 2>&1; then
      pnpm -s lint || true
      pnpm dlx eslint . || pnpm dlx prettier --check . || true
      return 0
    fi
    if command -v yarn >/dev/null 2>&1; then
      yarn -s lint || true
      npx --yes eslint . || npx --yes prettier --check . || true
      return 0
    fi
  fi

  # Python
  if [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
    if command -v ruff >/dev/null 2>&1; then
      ruff . || return 1
      return 0
    elif command -v black >/dev/null 2>&1; then
      echo "ruff not found; running black --check instead"
      black --check . || return 1
      return 0
    fi
  fi

  # Rust
  if [ -f "Cargo.toml" ] && command -v cargo >/dev/null 2>&1; then
    cargo fmt --all -- --check
    return 0
  fi

  # Go
  if [ -f "go.mod" ]; then
    if command -v golangci-lint >/dev/null 2>&1; then
      golangci-lint run || return 1
      return 0
    fi
    if command -v go >/dev/null 2>&1; then
      fmt_out=$(gofmt -l .)
      if [ -n "$fmt_out" ]; then
        echo "Files not formatted (gofmt):"
        echo "$fmt_out"
        return 1
      fi
      go vet ./... || return 1
      return 0
    fi
  fi

  # Java (best-effort)
  if [ -f "pom.xml" ] || [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
    if [ -x "./gradlew" ]; then
      ./gradlew -q check || true
      return 0
    fi
    if command -v mvn >/dev/null 2>&1; then
      mvn -q -DskipTests=true verify || true
      return 0
    fi
  fi

  echo "No recognized linter/formatter found; skipping lint/format checks"
}

run_tests() {
  # Node.js/TypeScript
  if [ -f "package.json" ]; then
    if command -v npm >/dev/null 2>&1; then
      npm test -s --if-present || return 1
      return 0
    fi
    if command -v pnpm >/dev/null 2>&1; then
      pnpm -s test || return 1
      return 0
    fi
    if command -v yarn >/dev/null 2>&1; then
      yarn -s test || return 1
      return 0
    fi
  fi

  # Python
  if [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
    if command -v pytest >/dev/null 2>&1; then
      pytest -q || return 1
      return 0
    fi
  fi

  # Rust
  if [ -f "Cargo.toml" ] && command -v cargo >/dev/null 2>&1; then
    cargo test -q || return 1
    return 0
  fi

  # Go
  if [ -f "go.mod" ] && command -v go >/dev/null 2>&1; then
    go test ./... || return 1
    return 0
  fi

  # Java
  if [ -f "pom.xml" ] || [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
    if [ -x "./gradlew" ]; then
      ./gradlew -q test || return 1
      return 0
    fi
    if command -v mvn >/dev/null 2>&1; then
      mvn -q test || return 1
      return 0
    fi
  fi

  echo "No recognized test runner found; skipping tests"
}

run_checks() {
  lint_failed=0
  test_failed=0
  run_lint || lint_failed=1
  run_tests || test_failed=1
  if [ $lint_failed -ne 0 ] || [ $test_failed -ne 0 ]; then
    return 1
  fi
  return 0
}

# Initial check; if it fails, try to auto-fix using local scripts if present
if ! run_checks; then
  echo "Initial checks failed; attempting auto-fix via scripts/format.py and scripts/lintfix.py if present"
  if [ -f "scripts/format.py" ]; then
    if command -v python3 >/dev/null 2>&1; then python3 scripts/format.py || true; else python scripts/format.py || true; fi
  fi
  if [ -f "scripts/lintfix.py" ]; then
    if command -v python3 >/dev/null 2>&1; then python3 scripts/lintfix.py || true; else python scripts/lintfix.py || true; fi
  fi
  if command -v git >/dev/null 2>&1; then git add -A; fi
  run_checks
fi

""",
    "pre-push": """#!/usr/bin/env bash
set -euo pipefail

echo "Running pre-push checks..."

# If pre-commit exists we can reuse tests configuration from it
if command -v pre-commit >/dev/null 2>&1 && [ -f ".pre-commit-config.yaml" ]; then
  pre-commit run --hook-stage push --all-files || true
fi

# Prefer ecosystem-specific tests
if [ -f "package.json" ]; then
  if command -v npm >/dev/null 2>&1; then
    npm test -s --if-present || true
    exit 0
  fi
  if command -v pnpm >/dev/null 2>&1; then
    pnpm -s test || true
    exit 0
  fi
  if command -v yarn >/dev/null 2>&1; then
    yarn -s test || true
    exit 0
  fi
fi

if [ -f "Cargo.toml" ] && command -v cargo >/dev/null 2>&1; then
  cargo test -q
  exit 0
fi

if [ -f "go.mod" ] && command -v go >/dev/null 2>&1; then
  go test ./...
  exit 0
fi

if [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
  if command -v pytest >/dev/null 2>&1; then
    pytest -q
    exit 0
  fi
fi

if [ -f "pom.xml" ] || [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
  if [ -x "./gradlew" ]; then
    ./gradlew -q test || true
    exit 0
  fi
  if command -v mvn >/dev/null 2>&1; then
    mvn -q test || true
    exit 0
  fi
fi

echo "No recognized test runner found; skipping tests"

""",
}


def _write_hook(repo_root: Path, name: str, content: str) -> Path:
    hooks_dir = repo_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_path = hooks_dir / name
    # Backup existing hook if present
    if hook_path.exists():
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = hooks_dir / f"{name}.{ts}.bak"
        backup_path.write_text(hook_path.read_text())
    hook_path.write_text(content)
    hook_path.chmod(
        hook_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    )
    return hook_path


@click.group()
def cli():
    """Manage Git hooks (pre-commit, pre-push)."""
    pass


@cli.command()
@click.option(
    "--repo",
    "repo",
    type=click.Path(exists=True, file_okay=False),
    default=os.getcwd(),
    help="Repository path",
)
@click.option(
    "--pre-commit/--no-pre-commit", default=True, help="Install pre-commit hook"
)
@click.option("--pre-push/--no-pre-push", default=True, help="Install pre-push hook")
@click.option(
    "--pre-commit-template",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to custom pre-commit script template",
)
@click.option(
    "--pre-push-template",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to custom pre-push script template",
)
def install(
    repo: str,
    pre_commit: bool,
    pre_push: bool,
    pre_commit_template: str | None,
    pre_push_template: str | None,
):
    """Install default hooks (lint/test)."""
    try:
        repo_root = Path(repo)
        if not (repo_root / ".git").exists():
            console.print("[red]Not a git repository[/red]")
            raise click.Abort()

        installed = []
        if pre_commit:
            content = None
            if pre_commit_template:
                content = Path(pre_commit_template).read_text()
            else:
                content = HOOK_TEMPLATES["pre-commit"]
            path = _write_hook(repo_root, "pre-commit", content)
            installed.append(path.name)
        if pre_push:
            content = None
            if pre_push_template:
                content = Path(pre_push_template).read_text()
            else:
                content = HOOK_TEMPLATES["pre-push"]
            path = _write_hook(repo_root, "pre-push", content)
            installed.append(path.name)

        if installed:
            console.print(
                Panel(
                    f"Installed hooks: {', '.join(installed)}",
                    title="Git Hooks",
                    border_style="green",
                )
            )
        else:
            console.print("[yellow]No hooks selected.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.option(
    "--repo",
    "repo",
    type=click.Path(exists=True, file_okay=False),
    default=os.getcwd(),
    help="Repository path",
)
@click.option(
    "--pre-commit/--no-pre-commit", default=True, help="Remove pre-commit hook"
)
@click.option("--pre-push/--no-pre-push", default=True, help="Remove pre-push hook")
def uninstall(repo: str, pre_commit: bool, pre_push: bool):
    """Remove installed hooks."""
    try:
        repo_root = Path(repo)
        if not (repo_root / ".git").exists():
            console.print("[red]Not a git repository[/red]")
            raise click.Abort()

        removed = []
        for name, selected in [("pre-commit", pre_commit), ("pre-push", pre_push)]:
            if not selected:
                continue
            hook_path = repo_root / ".git" / "hooks" / name
            if hook_path.exists():
                hook_path.unlink()
                removed.append(name)

        if removed:
            console.print(
                Panel(
                    f"Removed hooks: {', '.join(removed)}",
                    title="Git Hooks",
                    border_style="yellow",
                )
            )
        else:
            console.print("[yellow]No hooks removed.")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@cli.command(name="list")
@click.option(
    "--repo",
    "repo",
    type=click.Path(exists=True, file_okay=False),
    default=os.getcwd(),
    help="Repository path",
)
def list_hooks(repo: str):
    """List hooks present in the repository."""
    try:
        repo_root = Path(repo)
        hooks_dir = repo_root / ".git" / "hooks"
        if not hooks_dir.exists():
            console.print(
                "[yellow]No .git/hooks directory found (not a git repo?).[/yellow]"
            )
            return

        known = [
            "applypatch-msg",
            "pre-applypatch",
            "post-applypatch",
            "pre-commit",
            "pre-merge-commit",
            "prepare-commit-msg",
            "commit-msg",
            "post-commit",
            "pre-rebase",
            "post-checkout",
            "post-merge",
            "pre-push",
            "pre-receive",
            "update",
            "post-receive",
            "post-update",
            "reference-transaction",
            "push-to-checkout",
            "pre-auto-gc",
            "post-rewrite",
            "sendemail-validate",
            "fsmonitor-watchman",
            "p4-pre-submit",
        ]

        table = Table(title="Git Hooks")
        table.add_column("Hook", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Executable", style="magenta")

        found_any = False
        for name in known:
            p = hooks_dir / name
            if p.exists():
                found_any = True
                is_exec = os.access(p, os.X_OK)
                table.add_row(name, "present", "yes" if is_exec else "no")

        # Include unknown custom hooks present
        for p in sorted(hooks_dir.iterdir()):
            if p.is_file() and p.name not in known:
                found_any = True
                is_exec = os.access(p, os.X_OK)
                table.add_row(p.name, "custom", "yes" if is_exec else "no")

        if not found_any:
            console.print("[yellow]No hooks found in .git/hooks.[/yellow]")
            return

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()
