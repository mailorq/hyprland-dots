"""Validate generated Waybar profiles and the CSS contract.

This intentionally supplements, but never replaces, Waybar's own Linux parser.
It guards the project rules that Waybar itself cannot know: desktop hardware
privacy, explicit script dependencies, palette synchronization and geometry.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_theme_colors  # noqa: E402
import build_waybar_profiles  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"Waybar static contract: FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def exact(path: Path, expected: str) -> None:
    require(path.exists(), f"missing {path.relative_to(ROOT)}")
    actual = path.read_text(encoding="utf-8")
    require(actual == expected, f"generated adapter drift in {path.relative_to(ROOT)}")


def load_profile(profile_name: str) -> dict[str, object]:
    path = ROOT / "config" / "waybar" / f"config.{profile_name}.jsonc"
    exact(path, build_waybar_profiles.render_profile(profile_name))
    return json.loads(path.read_text(encoding="utf-8"))


def module_names(config: dict[str, object]) -> set[str]:
    names: set[str] = set()
    for placement in ("modules-left", "modules-center", "modules-right"):
        names.update(config[placement])  # type: ignore[arg-type]
    return names


def main() -> None:
    colors = build_theme_colors.load_palette()
    exact(ROOT / "config" / "waybar" / "fata" / "colors.css", build_theme_colors.css(colors))

    profiles = {
        name: load_profile(name)
        for name in build_waybar_profiles.PROFILES
    }
    desktop = profiles["desktop"]
    expected_left = ["custom/menu", "hyprland/workspaces", "hyprland/window"]
    expected_center = ["clock"]
    expected_right = ["pulseaudio", "network", "tray"]
    for name, config in profiles.items():
        require(config["height"] == 40, f"{name} must keep the 40 px bar height")
        require(config["margin-top"] == 8, f"{name} must keep the 8 px top margin")
        require(config["margin-left"] == 12, f"{name} must keep the 12 px outer margin")
        require(config["margin-right"] == 12, f"{name} must keep the 12 px outer margin")
        require(config["spacing"] == 0, f"{name} must let CSS own the 6 px cell gap")
        require(config["fixed-center"] is True, f"{name} must keep the clock centered")
        require(config["modules-left"] == expected_left, f"{name} left module order changed")
        require(config["modules-center"] == expected_center, f"{name} center module order changed")
        workspace = config["hyprland/workspaces"]  # type: ignore[index]
        require(workspace["persistent-workspaces"] == {"*": 10},
                f"{name} must expose exactly ten persistent workspaces")
        require(workspace["persistent-only"] is True,
                f"{name} must not surface special or transient workspaces")
        require(workspace["sort-by"] == "number", f"{name} must sort workspace numbers numerically")
        require(workspace["enable-bar-scroll"] is False,
                f"{name} must not switch workspaces while scrolling the panel")

    require(desktop["modules-right"] == expected_right, "desktop right module order changed")
    desktop_modules = module_names(desktop)
    forbidden_desktop = {
        "battery", "backlight", "temperature", "power-profiles-daemon", "cpu", "memory",
    }
    require(not desktop_modules & forbidden_desktop,
            "desktop profile must not expose hardware or performance monitoring")
    require(desktop["custom/menu"]["on-click"] == "/bin/sh -c 'exec \"$HOME/.local/bin/fata-rofi\"'",  # type: ignore[index]
            "the only custom module action must use the installed fata-rofi helper without PATH inheritance")
    require("exec" not in desktop["custom/menu"],  # type: ignore[operator]
            "menu must be static and must not spawn a polling helper")
    require("\n" in desktop["network"]["tooltip-format-wifi"],  # type: ignore[index]
            "network tooltip must contain a real newline, not a visible backslash-n")
    require(desktop["hyprland/window"]["fallback"] == "—",  # type: ignore[index]
            "window fallback must remain UTF-8 em dash, not a console-codepage artifact")

    expected_optional = {
        "desktop": (),
        "laptop-battery": ("battery",),
        "laptop-backlight": ("backlight",),
        "laptop-battery-backlight": ("battery", "backlight"),
    }
    for name, optional in expected_optional.items():
        expected = [*optional, *expected_right]
        require(profiles[name]["modules-right"] == expected,
                f"{name} optional hardware module order changed")
        names = module_names(profiles[name])
        require("temperature" not in names and "power-profiles-daemon" not in names,
                f"{name} must never infer temperature or power-profile monitoring")

    style_path = ROOT / "config" / "waybar" / "style.css"
    style = style_path.read_text(encoding="utf-8")
    for fragment in (
        '@import url("fata/colors.css");',
        "font-size: 12px;",
        "border: 2px solid @fm_border;",
        "border-radius: 8px;",
        "margin: 4px 3px;",
        "padding: 0 10px;",
        "min-width: 240px;",
        "#workspaces button.active",
        "#workspaces button.workspace-hover",
    ):
        require(fragment in style, f"Waybar CSS lacks {fragment!r}")
    forbidden_css = ("-gtk-", "box-shadow", "transition:", "@keyframes", "--")
    require(not any(fragment in style for fragment in forbidden_css),
            "Waybar CSS contains a GTK hack, animation, or CSS custom property")

    print("Waybar static contract: pass")


if __name__ == "__main__":
    main()
