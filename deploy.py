#!/usr/bin/env python3
"""
Deploy ai-daily-h5 to Vercel via CLI.
Includes HTML pages + generated images.
Usage: python3 deploy.py
"""
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent


def deploy():
    print("Deploying to Vercel...")

    # Git commit (ensure all changes are tracked)
    subprocess.run(
        ["git", "add", "-A"],
        cwd=str(BASE_DIR), capture_output=True, timeout=10,
    )
    subprocess.run(
        ["git", "commit", "-m", f"update", "--allow-empty"],
        cwd=str(BASE_DIR), capture_output=True, timeout=10,
    )

    result = subprocess.run(
        ["vercel", "--prod", "--yes"],
        cwd=str(BASE_DIR),
        capture_output=True,
        text=True,
        timeout=120,
    )

    for line in result.stdout.splitlines():
        line = line.strip()
        if "Production:" in line or "Aliased:" in line or "Error" in line:
            print(f"  {line}")

    if result.returncode != 0:
        print(f"  ERROR: {result.stderr.strip()}")
        return False

    # Ensure correct alias
    alias_result = subprocess.run(
        ["vercel", "alias", "set", "ai-agent-daily-phi.vercel.app", "lava-agent-daily.vercel.app"],
        cwd=str(BASE_DIR), capture_output=True, text=True, timeout=30,
    )
    if alias_result.returncode == 0:
        print("  https://lava-agent-daily.vercel.app ✅")

    return True


if __name__ == "__main__":
    ok = deploy()
    sys.exit(0 if ok else 1)
