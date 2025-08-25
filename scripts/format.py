#!/usr/bin/env python3
"""
Multi-ecosystem formatter runner.

Best-effort: formats sources if tools exist. Safe to run repeatedly.
"""
from __future__ import annotations

import os
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
    # Node/TS: prettier write
    if has_file("package.json"):
        if shutil.which("npm"):
            run(["npx", "--yes", "prettier", "--write", "."])  # type: ignore
        elif shutil.which("pnpm"):
            run(["pnpm", "dlx", "prettier", "--write", "."])  # type: ignore
        elif shutil.which("yarn"):
            run(["npx", "--yes", "prettier", "--write", "."])  # type: ignore

    # Python: ruff format or black
    if has_file("pyproject.toml", "requirements.txt"):
        if shutil.which("ruff"):
            run(["ruff", "format", "."])  # type: ignore
        elif shutil.which("black"):
            run(["black", "."])  # type: ignore

    # Rust: cargo fmt
    if has_file("Cargo.toml") and shutil.which("cargo"):
        run(["cargo", "fmt", "--all"])  # type: ignore

    # Go: gofmt -w
    if has_file("go.mod") and shutil.which("go"):
        # Format in-place; gofmt returns 0 even if files changed
        run(["gofmt", "-w", "."])  # type: ignore

    # Java: Gradle/Maven format plugins are not standard; skip
    return 0


if __name__ == "__main__":
    import shutil

    raise SystemExit(main())
