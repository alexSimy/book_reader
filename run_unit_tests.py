"""Lightweight test runner to execute our test functions without pytest.

This script imports the test modules we created and runs their test
functions directly. It prints a simple pass/fail summary.
"""
import asyncio
import importlib
import sys
import types

# Provide light-weight mocks for external binary-backed modules so tests
# can run in CI/environments without those native dependencies.
if 'fitz' not in sys.modules:
    class _Page:
        def get_text(self):
            return "DUMMY PAGE TEXT"

    class _Doc(list):
        def __init__(self):
            super().__init__([_Page()])

    fitz_mod = types.SimpleNamespace(open=lambda path: _Doc())
    sys.modules['fitz'] = fitz_mod

if 'llama_cpp' not in sys.modules:
    # Minimal fake llama_cpp module exposing a Llama class with create_completion
    import asyncio
    import importlib
    import sys
    import os

    # CI-only runner: exit with instructions when run locally without CI env vars.
    IS_CI = os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("CI") == "true"

    if not IS_CI:
        print("run_unit_tests.py is intended for CI environments.")
        print("To run tests locally use: python -m pytest -q")
        sys.exit(0)

    TEST_MODULES = [
        "tests.test_pdf_utils",
        "tests.test_book_agent",
    ]

    results = []

    for mod_name in TEST_MODULES:
        try:
            mod = importlib.import_module(mod_name)
        except Exception as e:
            print(f"ERROR importing {mod_name}: {e}")
            results.append((mod_name, False, f"import error: {e}"))
            continue

        for attr in dir(mod):
            if attr.startswith("test_"):
                fn = getattr(mod, attr)
                print(f"Running {mod_name}.{attr}()...")
                try:
                    # If the test is async, run via asyncio.run
                    if asyncio.iscoroutinefunction(fn):
                        asyncio.run(fn())
                    else:
                        fn()
                    print(f"  PASS: {mod_name}.{attr}")
                    results.append((f"{mod_name}.{attr}", True, ""))
                except Exception as e:
                    print(f"  FAIL: {mod_name}.{attr} -> {e}")
                    results.append((f"{mod_name}.{attr}", False, str(e)))

    print("\nTest summary:\n")
    passed = sum(1 for r in results if r[1])
    failed = sum(1 for r in results if not r[1])
    for r in results:
        status = "PASS" if r[1] else "FAIL"
        print(f"{status}: {r[0]} {('- ' + r[2]) if r[2] else ''}")

    print(f"\nTotal: {len(results)}  Passed: {passed}  Failed: {failed}")

    if failed:
        sys.exit(1)
    print(f"{status}: {r[0]} {('- ' + r[2]) if r[2] else ''}")

print(f"\nTotal: {len(results)}  Passed: {passed}  Failed: {failed}")

if failed:
    sys.exit(1)
