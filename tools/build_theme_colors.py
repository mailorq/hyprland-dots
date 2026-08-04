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


def main() -> None:
    colors = load_palette()
    (THEME_DIR / "colors.css").write_text(css(colors), encoding="utf-8")
    (THEME_DIR / "colors.conf").write_text(kitty(colors), encoding="utf-8")
    (THEME_DIR / "colors.rasi").write_text(rasi(colors), encoding="utf-8")
    (THEME_DIR / "colors.lua").write_text(lua(colors), encoding="utf-8")


if __name__ == "__main__":
    main()
