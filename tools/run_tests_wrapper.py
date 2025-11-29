#!/usr/bin/env python3
"""Wrapper to run the project's test runner using the repository `.venv` Python when available.

This helps pre-commit hooks (which run under the system Python) delegate test execution
to the project's virtual environment where pytest and other dev dependencies are installed.

Usage: python tools/run_tests_wrapper.py [pytest args]
"""
from __future__ import annotations

import os
import sys
import subprocess


def find_repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_venv_python(repo_root: str) -> str | None:
    # Check common venv locations (Windows and Unix)
    candidates = [
        os.path.join(repo_root, '.venv', 'Scripts', 'python.exe'),
        os.path.join(repo_root, '.venv', 'bin', 'python'),
        os.path.join(repo_root, '..', '.venv', 'Scripts', 'python.exe'),
        os.path.join(repo_root, '..', '.venv', 'bin', 'python'),
    ]
    for p in candidates:
        p = os.path.abspath(p)
        if os.path.exists(p):
            return p
    return None


def run_with_venv(venv_python: str, args: list[str]) -> int:
    repo_root = find_repo_root()
    runtest = os.path.join(repo_root, 'runtest.py')
    cmd = [venv_python, runtest] + args
    print('Running tests with venv python:', venv_python)
    return subprocess.call(cmd)


def run_with_import(args: list[str]) -> int:
    # Try to import pytest in current interpreter and run it
    try:
        import pytest
    except Exception:
        return -1
    print('Running pytest via import in current Python interpreter')
    return pytest.main(args)


def run_with_system_pytest(args: list[str]) -> int:
    cmd = [sys.executable, '-m', 'pytest'] + args
    print('Falling back to system python:', sys.executable)
    return subprocess.call(cmd)


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    repo_root = find_repo_root()
    venv_python = find_venv_python(repo_root)
    if venv_python:
        try:
            return run_with_venv(venv_python, argv)
        except Exception as e:
            print('Error running with venv python:', e)

    rc = run_with_import(argv)
    if rc is not None and rc >= 0:
        return rc

    return run_with_system_pytest(argv)


if __name__ == '__main__':
    sys.exit(main())
