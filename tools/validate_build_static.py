"""Validate the POSIX builder's safety boundary and orchestration contract."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "fata-build"


def fail(message: str) -> None:
    raise SystemExit(f"Build static contract: FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    text = BUILDER.read_text(encoding="utf-8")
    require(text.startswith("#!/bin/sh\n"), "builder must use POSIX sh")
    require("set -eu" in text, "builder must fail on unset variables and command errors")
    require("fm_mode=check" in text, "builder must default to non-mutating validation")
    require("${PYTHON:-python3}" in text, "builder must permit an explicit Python command")
    require(
        'fm_python_script=$1\n    shift\n    "$fm_python" "$fm_root/$fm_python_script" "$@"' in text,
        "builder must forward arguments to the selected Python tool",
    )
    for mode in ("--check", "--refresh-generated", "--integration"):
        require(mode in text, f"builder lacks {mode} mode")
    for script in (
        "tools/build_theme_colors.py",
        "tools/build_art_selectors.py",
        "tools/build_waybar_profiles.py",
        "tools/build_release_manifest.py",
        "tools/validate_release.py",
    ):
        require(script in text, f"builder does not orchestrate {script}")
    for forbidden in (
        "tools/build_art_assets.py",
        "tools/build_wallpapers.py",
        "--rebuild-frozen-assets",
    ):
        require(forbidden not in text, f"builder must not expose frozen asset writes: {forbidden}")
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    require("theme/colors.* text eol=lf" in attributes,
            "generated theme adapters must retain LF line endings across checkouts")
    print("Build static contract: pass")


if __name__ == "__main__":
    main()
