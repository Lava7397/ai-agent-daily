#!/usr/bin/env python3
"""Deploy ai-daily-h5 to Vercel via CLI.

Thin wrapper over `vercel --prod --yes` so the deploy command is the same
locally and in automation. Intentionally does NOT make git commits —
commits must be created explicitly by whoever changes the code or data.

Custom domain (lava7397.com) is configured in the Vercel dashboard and
does not require any alias command here.

Usage: python3 deploy.py
"""
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent


def deploy() -> bool:
    print("Deploying to Vercel...")
    result = subprocess.run(
        ["vercel", "--prod", "--yes"],
        cwd=str(BASE_DIR),
        capture_output=True,
        text=True,
        timeout=180,
    )

    for line in result.stdout.splitlines():
        line = line.strip()
        if "Production:" in line or "Preview:" in line or "Error" in line:
            print(f"  {line}")

    if result.returncode != 0:
        print(f"  ERROR: {result.stderr.strip()}", file=sys.stderr)
        return False

    print("  Deploy OK ✅")
    return True


if __name__ == "__main__":
    sys.exit(0 if deploy() else 1)
