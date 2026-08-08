"""Render application adapters from the canonical Fata Morgana palette.

This script uses only Python's standard library. Do not hand-edit the generated
files: update theme/palette.json and rerun this program instead.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PALETTE_PATH = ROOT / "theme" / "palette.json"
THEME_DIR = ROOT / "theme"
HYPRLAND_COLORS_PATH = ROOT / "config" / "hypr" / "fata" / "colors.lua"
KITTY_COLORS_PATH = ROOT / "config" / "kitty" / "fata" / "colors.conf"
ROFI_COLORS_PATH = ROOT / "config" / "rofi" / "fata" / "colors.rasi"
MAKO_CONFIG_PATH = ROOT / "config" / "mako" / "config"
WAYBAR_COLORS_PATH = ROOT / "config" / "waybar" / "fata" / "colors.css"
TOKEN_ORDER = (
    "black", "bg_deep", "bg", "bg_cool", "surface", "surface_warm",
    "border", "fg_dim", "fg_muted", "fg", "white", "burgundy",
    "burgundy_active", "brass", "brass_bright", "storm", "moss", "danger",
)


def load_palette() -> dict[str, str]:
    palette = json.loads(PALETTE_PATH.read_text(encoding="utf-8"))
    colors = palette["colors"]
    if tuple(colors) != TOKEN_ORDER:
        raise ValueError("palette token order or names differ from the color contract")
    for name, value in colors.items():
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
            raise ValueError(f"{name} is not a six-digit hexadecimal color: {value!r}")
    return colors


def css(colors: dict[str, str]) -> str:
    lines = [
        "/* Generated from theme/palette.json by tools/build_theme_colors.py. */",
        "/* GTK 3 supports named colors; CSS custom properties are intentionally absent. */",
    ]
    lines.extend(f"@define-color fm_{name} {value};" for name, value in colors.items())
    return "\n".join(lines) + "\n"


def kitty(colors: dict[str, str]) -> str:
    values = {
        "background": colors["bg"],
        "foreground": colors["fg"],
        "selection_background": colors["border"],
        "selection_foreground": colors["white"],
        "cursor": colors["brass_bright"],
        "cursor_text_color": colors["bg"],
        "url_color": colors["storm"],
        "color0": colors["bg_deep"],
        "color1": colors["danger"],
        "color2": colors["moss"],
        "color3": colors["brass"],
        "color4": colors["storm"],
        "color5": colors["burgundy_active"],
        "color6": colors["storm"],
        "color7": colors["fg_muted"],
        "color8": colors["border"],
        "color9": colors["danger"],
        "color10": colors["moss"],
        "color11": colors["brass_bright"],
        "color12": colors["storm"],
        "color13": colors["burgundy_active"],
        "color14": colors["storm"],
        "color15": colors["white"],
    }
    lines = [
        "# Generated from theme/palette.json by tools/build_theme_colors.py.",
        "# This file contains only Kitty color keys and is safe to include directly.",
    ]
    lines.extend(f"{key} {value}" for key, value in values.items())
    return "\n".join(lines) + "\n"


def rasi(colors: dict[str, str]) -> str:
    lines = [
        "/* Generated from theme/palette.json by tools/build_theme_colors.py. */",
        "/* Rasi named values use @fm-... references in concrete Rofi widgets. */",
        "* {",
    ]
    lines.extend(f"    fm-{name.replace('_', '-')}: {value};" for name, value in colors.items())
    lines.append("}")
    return "\n".join(lines) + "\n"


def lua(colors: dict[str, str]) -> str:
    lines = [
        "-- Generated from theme/palette.json by tools/build_theme_colors.py.",
        "-- Hyprland 0.55+ accepts web-style hexadecimal colors in Lua configs.",
        "return {",
    ]
    lines.extend(f'    {name} = "{value}",' for name, value in colors.items())
    lines.append("}")
    return "\n".join(lines) + "\n"


def mako(colors: dict[str, str]) -> str:
    """Render Mako's complete, XDG-portable key-value configuration."""
    alpha = lambda name: f"{colors[name]}FF"
    return "\n".join((
        "# Generated from theme/palette.json by tools/build_theme_colors.py.",
        "# Do not hand-edit: Mako include paths cannot portably follow XDG_CONFIG_HOME.",
        "max-history=20",
        "sort=-time",
        "layer=top",
        "anchor=top-right",
        "width=380",
        "height=160",
        "outer-margin=8",
        "margin=4",
        "padding=12",
        "border-size=2",
        "border-radius=8",
        "font=sans-serif 11",
        "markup=1",
        "format=<b>%s</b>\\n%b",
        "text-alignment=left",
        "icons=1",
        "icon-location=left",
        "max-icon-size=40",
        "icon-border-radius=6",
        "actions=1",
        "default-timeout=6000",
        "ignore-timeout=0",
        "max-visible=3",
        "on-button-left=invoke-default-action",
        "on-button-right=dismiss",
        "",
        f"background-color={alpha('bg')}",
        f"text-color={alpha('fg')}",
        f"border-color={alpha('brass')}",
        f"progress-color=over {alpha('brass_bright')}",
        "",
        "[urgency=low]",
        f"border-color={alpha('storm')}",
        f"text-color={alpha('fg_muted')}",
        "",
        "[urgency=normal]",
        f"border-color={alpha('brass')}",
        "",
        "[urgency=high]",
        f"background-color={alpha('burgundy')}",
        f"border-color={alpha('danger')}",
        f"text-color={alpha('white')}",
        f"progress-color=over {alpha('danger')}",
        "default-timeout=0",
        "ignore-timeout=1",
        "",
    ))


def main() -> None:
    colors = load_palette()
    outputs = {
        THEME_DIR / "colors.css": css(colors),
        THEME_DIR / "colors.conf": kitty(colors),
        THEME_DIR / "colors.rasi": rasi(colors),
        THEME_DIR / "colors.lua": lua(colors),
        HYPRLAND_COLORS_PATH: lua(colors),
        KITTY_COLORS_PATH: kitty(colors),
        ROFI_COLORS_PATH: rasi(colors),
        MAKO_CONFIG_PATH: mako(colors),
        WAYBAR_COLORS_PATH: css(colors),
    }
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
