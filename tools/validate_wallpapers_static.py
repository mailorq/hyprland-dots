"""Validate the curated wallpaper exports and their Hyprpaper integration."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_wallpapers  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"Wallpaper static contract: FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    require(build_wallpapers.verify(build_wallpapers.OUTPUT_DIR) == 0,
            "wallpaper exports are invalid")

    config_path = ROOT / "config" / "hypr" / "hyprpaper.conf"
    config = config_path.read_text(encoding="utf-8")
    for fragment in (
        "splash = false",
        "ipc = true",
        "wallpaper {",
        "monitor =",
        "path = ~/.local/share/fata-morgana/wallpapers/fata-morgana-016-violet-cloaked-portrait-wallpaper-16x9.jpg",
        "fit_mode = cover",
    ):
        require(fragment in config, f"hyprpaper config lacks {fragment!r}")
    require(not any(fragment in config for fragment in ("preload", "reload", "unload", "listloaded")),
            "hyprpaper config contains a deprecated request")

    autostart = (ROOT / "config" / "hypr" / "fata" / "autostart.lua").read_text(encoding="utf-8")
    require('hl.exec_cmd("hyprpaper")' in autostart,
            "Hyprland session does not launch the declared wallpaper backend")

    installer = (ROOT / "scripts" / "fata-install").read_text(encoding="utf-8")
    for fragment in (
        "fm_require_command hyprpaper",
        'config/hypr/hyprpaper.conf',
        "assets/wallpapers/fata-morgana/*.jpg",
    ):
        require(fragment in installer, f"installer lacks wallpaper route or dependency: {fragment!r}")

    print("Wallpaper static contract: pass")


if __name__ == "__main__":
    main()
