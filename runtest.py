#!/usr/bin/env python3
"""Run the project's pytest suite with `src` on PYTHONPATH.

Usage:
  python runtest.py [pytest args]

This script will try to import `pytest` and call `pytest.main()`; if pytest
is not installed in the current interpreter it falls back to running
`python -m pytest` via subprocess. It also ensures `src/` is on sys.path so
tests can import `src` packages.
"""
from __future__ import annotations

import os
import sys
import subprocess


def ensure_src_on_path():
    repo_root = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(repo_root, "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    # Also set PYTHONPATH in environment for subprocesses
    env_pythonpath = os.environ.get("PYTHONPATH", "")
    parts = env_pythonpath.split(os.pathsep) if env_pythonpath else []
    if src_path not in parts:
        parts.insert(0, src_path)
        os.environ["PYTHONPATH"] = os.pathsep.join(parts)


def load_dotenv_file():
    """Lightweight .env loader: read key=value lines and set them in os.environ.

    This avoids an external dependency and ensures subprocesses inherit the vars.
    """
    repo_root = os.path.dirname(os.path.abspath(__file__))
    dotenv_path = os.path.join(repo_root, ".env")
    if not os.path.exists(dotenv_path):
        return

    with open(dotenv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            # Only set if not already present in the environment
            if key not in os.environ:
                os.environ[key] = val


def run_pytest_via_import(pytest_args: list[str]) -> int:
    try:
        import pytest

        print("Running pytest via import with args:", pytest_args)
        return pytest.main(pytest_args)
    except Exception as e:  # includes ImportError
        print("Could not run pytest via import (missing/errored):", e)
        return -1


def run_pytest_via_subprocess(pytest_args: list[str]) -> int:
    cmd = [sys.executable, "-m", "pytest"] + pytest_args
    print("Running pytest via subprocess:", " ".join(cmd))
    p = subprocess.run(cmd, env=os.environ)
    return p.returncode


def main():
    ensure_src_on_path()
    args = sys.argv[1:]
    # default to quiet mode
    if not args:
        args = ["-q"]

    rc = run_pytest_via_import(args)
    if rc is None or rc < 0:
        rc = run_pytest_via_subprocess(args)

    sys.exit(rc)


if __name__ == "__main__":
    main()
