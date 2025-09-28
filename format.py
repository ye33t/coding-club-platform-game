#!/usr/bin/env python3
"""Format and lint the codebase."""

import subprocess
import sys


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return True if successful."""
    print(f"\n{'=' * 60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        if result.returncode != 0:
            print(f"[FAILED] {description} failed with exit code {result.returncode}")
            return False
        else:
            print(f"[OK] {description} completed successfully")
            return True
    except FileNotFoundError:
        print(f"[ERROR] Command not found: {cmd[0]}")
        print("   Make sure you've run: poetry install")
        return False


def main():
    """Run all formatting and linting tools."""
    # Define paths to format/check
    python_paths = ["game", "main.py", "format.py", "sprite_extractor.py"]

    # Track success
    all_success = True

    # Run isort
    isort_cmd = ["poetry", "run", "isort"] + python_paths
    if not run_command(isort_cmd, "isort (import sorting)"):
        all_success = False

    # Run black
    black_cmd = ["poetry", "run", "black"] + python_paths
    if not run_command(black_cmd, "black (code formatting)"):
        all_success = False

    # Run flake8
    flake8_cmd = ["poetry", "run", "flake8"] + python_paths
    if not run_command(flake8_cmd, "flake8 (linting)"):
        all_success = False

    # Run mypy
    mypy_cmd = ["poetry", "run", "mypy"] + python_paths
    if not run_command(mypy_cmd, "mypy (type checking)"):
        all_success = False

    # Final report
    print(f"\n{'=' * 60}")
    if all_success:
        print("[SUCCESS] All formatting and linting checks passed!")
    else:
        print("[FAILED] Some checks failed. Please review the output above.")
    print("=" * 60)

    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())
