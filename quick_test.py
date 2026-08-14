#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(label: str, *args: str) -> None:
    print(f"\n=== {label} ===")
    result = subprocess.run([sys.executable, *args], cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    try:
        import fastapi  # noqa: F401
        import httpx  # noqa: F401
    except ImportError:
        print("Missing gateway test dependencies.")
        print(f"Run: {sys.executable} -m pip install -r gateway/requirements.txt")
        raise SystemExit(2)

    run(
        "Experience dry-run",
        "submit.py",
        "--type", "experience",
        "--file", "skills/fortior-knowledge-contributor/examples/experience-example.json",
        "--dry-run",
    )
    run(
        "Review Point dry-run",
        "submit.py",
        "--type", "review_point",
        "--file", "skills/fortior-knowledge-contributor/examples/review-point-example.json",
        "--dry-run",
    )
    run("Gateway mock integration", "gateway/test_gateway.py")

    print("\nALL LOCAL SMOKE TESTS: PASS")


if __name__ == "__main__":
    main()
