"""Validate the v1 release manifest and frozen-asset write guards."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_art_assets  # noqa: E402
import build_release_manifest  # noqa: E402
import build_wallpapers  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"Release static contract: FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    require(version == "1.0.0", "v1 release line must declare VERSION 1.0.0")
    expected = build_release_manifest.render()
    actual_path = ROOT / "assets" / "deployment.sha256"
    require(actual_path.is_file(), "missing deployment checksum manifest")
    require(b"\r" not in actual_path.read_bytes(), "deployment checksum manifest must use LF line endings")
    require(actual_path.read_text(encoding="utf-8") == expected, "deployment checksum manifest is out of date")

    paths = build_release_manifest.deployment_paths()
    require(len(paths) == len(set(paths)), "deployment checksum inventory contains duplicates")
    require(all("pictures" not in path.parts for path in paths), "private raw references must not enter deployment")
    require(all(not path.is_symlink() for path in paths), "deployment inventory must not contain symlinks")

    art_source = (ROOT / "tools" / "build_art_assets.py").read_text(encoding="utf-8")
    wallpaper_source = (ROOT / "tools" / "build_wallpapers.py").read_text(encoding="utf-8")
    require("--rebuild-frozen-assets" in art_source, "art builder must gate frozen-asset writes")
    require("--rebuild-frozen-assets" in wallpaper_source, "wallpaper builder must gate frozen-asset writes")
    integration_test = (ROOT / "tools" / "test_install_integration.sh").read_text(encoding="utf-8")
    require("fm_test_root=$(mktemp -d)" in integration_test,
            "installer integration test must create its own temporary root")
    require(integration_test.count('rm -rf "$fm_test_root"') == 1,
            "installer integration test may only remove its own mktemp root")
    release_gate = (ROOT / "tools" / "validate_release.py").read_text(encoding="utf-8")
    require('checks.append(("sh", "tools/test_install_integration.sh"))' in release_gate,
            "release gate must include the shell integration test when requested")
    require('command = list(check) if check[0] == "sh" else [sys.executable, *check]' in release_gate,
            "release gate must not execute the shell integration test through Python")
    require(build_art_assets.verify(build_art_assets.DEFAULT_INPUT_DIR, build_art_assets.DEFAULT_OUTPUT_DIR) == 0,
            "frozen art masters failed verification")
    require(build_wallpapers.verify(build_wallpapers.OUTPUT_DIR) == 0,
            "frozen wallpapers failed verification")

    print("Release static contract: pass")


if __name__ == "__main__":
    main()
