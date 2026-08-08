"""Render the supported Waybar hardware profiles.

The output is strict JSON despite the .jsonc extension accepted by Waybar.  This
makes the generated profiles easy to validate without a comment stripper.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WAYBAR_DIR = ROOT / "config" / "waybar"
PROFILES = {
    "desktop": (),
    "laptop-battery": ("battery",),
    "laptop-backlight": ("backlight",),
    "laptop-battery-backlight": ("battery", "backlight"),
}


def module_definitions() -> dict[str, dict[str, object]]:
    """Return only modules that need a configuration object."""
    return {
        "custom/menu": {
            "format": "MENU",
            "tooltip": False,
            "on-click": "/bin/sh -c 'exec \"$HOME/.local/bin/fata-rofi\"'",
        },
        "hyprland/workspaces": {
            "format": "{name}",
            "persistent-only": True,
            "persistent-workspaces": {"*": 10},
            "all-outputs": False,
            "move-to-monitor": True,
            "enable-bar-scroll": False,
            "sort-by": "number",
            "tooltip": False,
        },
        "hyprland/window": {
            "max-length": 46,
            "separate-outputs": True,
            "fallback": "—",
            "tooltip": True,
            "tooltip-format": "{title}",
        },
        "clock": {
            "interval": 60,
            "format": "{:%H:%M}",
            "tooltip": True,
            "tooltip-format": "{:%A, %d %B %Y}",
        },
        "pulseaudio": {
            "format": "VOL {volume}%",
            "format-muted": "MUTED",
            "scroll-step": 2,
            "max-volume": 100,
            "tooltip": True,
            "tooltip-format": "{desc}: {volume}%",
        },
        "network": {
            "interval": 5,
            "format-wifi": "WLAN {signalStrength}%",
            "format-ethernet": "LAN",
            "format-linked": "LINK",
            "format-disconnected": "OFFLINE",
            "format-disabled": "WLAN OFF",
            "tooltip": True,
            "tooltip-format-wifi": "{essid} ({signalStrength}%)\n{ipaddr}",
            "tooltip-format-ethernet": "{ifname}\n{ipaddr}",
            "tooltip-format-disconnected": "Network disconnected",
        },
        "tray": {
            "icon-size": 16,
            "spacing": 6,
            "show-passive-items": False,
        },
        "battery": {
            "interval": 60,
            "states": {"warning": 25, "critical": 12},
            "format": "BAT {capacity}%",
            "format-charging": "CHG {capacity}%",
            "format-plugged": "AC {capacity}%",
            "tooltip": True,
            "tooltip-format": "Battery: {capacity}% ({timeTo})",
        },
        "backlight": {
            "interval": 5,
            "format": "LIGHT {percent}%",
            "tooltip": True,
            "tooltip-format": "Display brightness: {percent}%",
        },
    }


def profile(profile_name: str) -> dict[str, object]:
    """Build one bar configuration from an explicit optional-module set."""
    optional = PROFILES[profile_name]
    right = [*optional, "pulseaudio", "network", "tray"]
    result: dict[str, object] = {
        "layer": "top",
        "position": "top",
        "height": 40,
        "margin-top": 8,
        "margin-left": 12,
        "margin-right": 12,
        "spacing": 0,
        "fixed-center": True,
        "modules-left": ["custom/menu", "hyprland/workspaces", "hyprland/window"],
        "modules-center": ["clock"],
        "modules-right": right,
    }
    definitions = module_definitions()
    for name in [*result["modules-left"], *result["modules-center"], *right]:
        if name in definitions:
            result[name] = definitions[name]
    return result


def render_profile(profile_name: str) -> str:
    if profile_name not in PROFILES:
        raise ValueError(f"unknown Waybar profile: {profile_name}")
    return json.dumps(profile(profile_name), indent=2, ensure_ascii=False) + "\n"


def main() -> None:
    for profile_name in PROFILES:
        target = WAYBAR_DIR / f"config.{profile_name}.jsonc"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_profile(profile_name), encoding="utf-8")


if __name__ == "__main__":
    main()
