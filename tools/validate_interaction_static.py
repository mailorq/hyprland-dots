"""Check reproducible contracts for Kitty, Rofi, Mako and Fata artwork.

This is deliberately a static check. It cannot replace Kitty/Rofi/Mako's own
parsers on the future Linux target, but it detects adapter drift, unapproved
artwork references, legacy GTK-CSS fragments and accidental runtime helpers.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_art_selectors  # noqa: E402
import build_theme_colors  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"Interaction-surface static contract: FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def exact(path: Path, expected: str) -> None:
    require(path.exists(), f"missing {path.relative_to(ROOT)}")
    actual = path.read_text(encoding="utf-8")
    require(actual == expected, f"generated adapter drift in {path.relative_to(ROOT)}")


def requires_value_error(artwork: object, description: str) -> None:
    try:
        build_art_selectors.validate_artwork(artwork)
    except ValueError:
        return
    fail(f"art selector accepted malformed catalogue: {description}")


def main() -> None:
    colors = build_theme_colors.load_palette()
    exact(ROOT / "config" / "kitty" / "fata" / "colors.conf", build_theme_colors.kitty(colors))
    exact(ROOT / "config" / "rofi" / "fata" / "colors.rasi", build_theme_colors.rasi(colors))
    exact(ROOT / "config" / "mako" / "config", build_theme_colors.mako(colors))

    artwork = build_art_selectors.load_artwork()
    filenames = sorted(str(item["file"]) for item in artwork)
    default = build_art_selectors.default_filename(artwork)
    duplicate_id = [dict(item) for item in artwork]
    duplicate_id[1]["id"] = duplicate_id[0]["id"]
    requires_value_error(duplicate_id, "duplicate artwork ID")
    mismatched_index = [dict(item) for item in artwork]
    mismatched_index[0]["id"] = "fm-999"
    requires_value_error(mismatched_index, "ID/filename index mismatch")
    duplicate_role = [dict(item) for item in artwork]
    duplicate_role[0]["roles"] = ["kitty", "rofi", "rofi"]
    requires_value_error(duplicate_role, "duplicate role")
    for unsafe_filename in (
        "../outside.jpg",
        "fata-morgana-001-$(touch-pwned).jpg",
        'fata-morgana-001-quote".jpg',
        "fata-morgana-001-newline\n.jpg",
    ):
        try:
            build_art_selectors.rofi_launcher([unsafe_filename], unsafe_filename)
        except ValueError:
            pass
        else:
            fail(f"art selector accepted shell-unsafe filename: {unsafe_filename!r}")
    exact(ROOT / "config" / "kitty" / "fata" / "art.conf", build_art_selectors.kitty_config())
    exact(ROOT / "config" / "rofi" / "fata" / "art.rasi", build_art_selectors.rofi_theme())
    expected_rofi_launcher = build_art_selectors.rofi_launcher(filenames, default)
    require("|\n" not in expected_rofi_launcher,
            "Rofi launcher must not split POSIX case alternatives after a pipe")
    exact(ROOT / "scripts" / "fata-rofi", expected_rofi_launcher)

    manifest = json.loads(
        (ROOT / "assets" / "art" / "fata-morgana" / "manifest.json").read_text(encoding="utf-8")
    )
    require(len(artwork) == 40, "approved artwork count must remain 40")
    require(
        all("kitty" in item["roles"] and "rofi" in item["roles"] for item in artwork),
        "each approved master must remain selectable by Kitty and Rofi",
    )
    require(
        all((ROOT / "assets" / "art" / "fata-morgana" / filename).is_file() for filename in filenames),
        "manifest refers to a missing normalized artwork master",
    )
    require(manifest["schema_version"] == 1, "unexpected artwork manifest schema")

    kitty_entry = (ROOT / "config" / "kitty" / "kitty.conf").read_text(encoding="utf-8")
    kitty_layout = (ROOT / "config" / "kitty" / "fata" / "layout.conf").read_text(encoding="utf-8")
    kitty_art = (ROOT / "config" / "kitty" / "fata" / "art.conf").read_text(encoding="utf-8")
    for fragment in (
        "include fata/colors.conf",
        "include fata/layout.conf",
        "include fata/art.conf",
        "globinclude fata/local/*.conf",
    ):
        require(fragment in kitty_entry, f"Kitty entry point lacks {fragment!r}")
    for fragment in ("font_family monospace", "font_size 12.0", "window_padding_width 10"):
        require(fragment in kitty_layout, f"Kitty layout lacks {fragment!r}")
    for fragment in (
        "background_image ${HOME}/.local/share/fata-morgana/art/*.jpg",
        "background_image_layout cscaled",
        "background_tint 0.60",
    ):
        require(fragment in kitty_art, f"Kitty art selector lacks {fragment!r}")
    require("allow_remote_control" not in kitty_entry + kitty_layout + kitty_art,
            "Kitty remote control must not be enabled implicitly")

    rofi_entry = (ROOT / "config" / "rofi" / "config.rasi").read_text(encoding="utf-8")
    rofi_theme = (ROOT / "config" / "rofi" / "fata.rasi").read_text(encoding="utf-8")
    require('@theme "fata.rasi"' in rofi_entry, "Rofi entry point does not load Fata theme")
    for fragment in (
        '@import "fata/colors.rasi"',
        '@import "fata/art.rasi"',
        "width: 42%;",
        "background-image: @fm-rofi-art;",
        "lines: 7;",
        "@media ( min-width: 2200px )",
        "lines: 9;",
    ):
        require(fragment in rofi_theme, f"Rofi theme lacks {fragment!r}")
    forbidden_rasi = ("@define-color", "-gtk-", "box-shadow", "transition:")
    require(
        not any(fragment in rofi_entry + rofi_theme for fragment in forbidden_rasi),
        "Rofi contains a GTK/CSS-only property rather than valid Rasi",
    )

    mako_config = (ROOT / "config" / "mako" / "config").read_text(encoding="utf-8")
    for fragment in (
        "width=380",
        "height=160",
        "outer-margin=8",
        "margin=4",
        "padding=12",
        "border-size=2",
        "border-radius=8",
        "max-visible=3",
    ):
        require(fragment in mako_config, f"Mako config lacks {fragment!r}")
    require(
        "[urgency=high]" in mako_config
        and "default-timeout=0" in mako_config
        and "ignore-timeout=1" in mako_config,
        "Mako high urgency must remain persistent even if a client specifies a timeout",
    )
    require("include=" not in mako_config,
            "Mako must not hard-code a non-portable XDG include path")
    require("exec " not in mako_config, "Mako must not introduce an undeclared command dependency")

    print("Interaction-surface static contract: pass")


if __name__ == "__main__":
    main()
