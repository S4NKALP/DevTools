#!/usr/bin/env python3
"""
Multi-ecosystem lint fixer.

Best-effort: applies automatic fixes if tools exist. Safe to run repeatedly.
"""
from __future__ import annotations

import subprocess
from pathlib import Path


def has_file(*names: str) -> bool:
    return any((Path.cwd() / name).exists() for name in names)


def run(cmd: list[str]) -> int:
    try:
        return subprocess.run(cmd, check=False).returncode
    except Exception:
        return 0


def main() -> int:
    import shutil

    # Node/TS: eslint --fix and prettier --write
    if has_file("package.json"):
        if shutil.which("npx"):
            run(["npx", "--yes", "eslint", "--fix", "."])  # type: ignore
            run(["npx", "--yes", "prettier", "--write", "."])  # type: ignore
        elif shutil.which("pnpm"):
            run(["pnpm", "dlx", "eslint", "--fix", "."])  # type: ignore
            run(["pnpm", "dlx", "prettier", "--write", "."])  # type: ignore

    # Python: ruff --fix or autoflake + isort + black
    if has_file("pyproject.toml", "requirements.txt"):
        if shutil.which("ruff"):
            run(["ruff", "check", "--fix", "."])  # type: ignore
        else:
            if shutil.which("autoflake"):
                run(["autoflake", "-r", "--in-place", "--remove-all-unused-imports", "."])  # type: ignore
            if shutil.which("isort"):
                run(["isort", "."])  # type: ignore
            if shutil.which("black"):
                run(["black", "."])  # type: ignore

    # Go: go fmt and go fix
    if has_file("go.mod") and shutil.which("go"):
        run(["go", "fmt", "./..."])  # type: ignore
        run(["go", "fix", "./..."])  # type: ignore

    # Rust: cargo clippy --fix (requires nightly for some fixes; allow failure)
    if has_file("Cargo.toml") and shutil.which("cargo"):
        run(["cargo", "clippy", "--fix", "-Z", "unstable-options", "--allow-dirty", "--allow-staged"])  # type: ignore

    # Java: no standard auto-fix; skip

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
