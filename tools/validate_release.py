"""Run the complete non-mutating v1 release gate."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKS = (
    ("tools/build_art_assets.py", "--check"),
    ("tools/build_wallpapers.py", "--check"),
    ("tools/build_release_manifest.py", "--check"),
    ("tools/validate_hyprland_static.py",),
    ("tools/validate_interaction_static.py",),
    ("tools/validate_waybar_static.py",),
    ("tools/validate_wallpapers_static.py",),
    ("tools/validate_install_static.py",),
    ("tools/validate_build_static.py",),
    ("tools/validate_release_static.py",),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--integration",
        action="store_true",
        help="also run the isolated POSIX-shell installer integration test",
    )
    args = parser.parse_args()
    checks = list(CHECKS)
    if args.integration:
        checks.append(("sh", "tools/test_install_integration.sh"))
    for check in checks:
        command = list(check) if check[0] == "sh" else [sys.executable, *check]
        print("+", " ".join(command))
        completed = subprocess.run(command, cwd=ROOT, check=False)
        if completed.returncode != 0:
            return completed.returncode
    print("Release gate: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
