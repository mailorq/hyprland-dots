"""Generate application-side artwork selectors from the approved manifest.

The generated Rofi launcher intentionally uses only POSIX ``sh`` and the
mandatory ``rofi`` binary at runtime.  It does not scan directories or invoke
random-selection utilities: the manifest is the allowlist.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "assets" / "art" / "fata-morgana" / "manifest.json"
KITTY_ART_PATH = ROOT / "config" / "kitty" / "fata" / "art.conf"
ROFI_ART_PATH = ROOT / "config" / "rofi" / "fata" / "art.rasi"
ROFI_LAUNCHER_PATH = ROOT / "scripts" / "fata-rofi"
DATA_ART_DIR = "${HOME}/.local/share/fata-morgana/art"
DEFAULT_ART_ID = "fm-038"


def load_artwork() -> list[dict[str, object]]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    artwork = manifest["artwork"]
    if not isinstance(artwork, list) or not artwork:
        raise ValueError("art manifest contains no artwork")

    filenames: set[str] = set()
    for item in artwork:
        roles = item.get("roles", [])
        filename = item.get("file")
        if not isinstance(filename, str) or not filename.endswith(".jpg"):
            raise ValueError(f"invalid generated artwork filename: {filename!r}")
        if filename in filenames:
            raise ValueError(f"duplicate generated artwork filename: {filename}")
        if "kitty" not in roles or "rofi" not in roles:
            raise ValueError(f"{item.get('id')} is missing a Kitty or Rofi role")
        filenames.add(filename)
    return artwork


def default_filename(artwork: list[dict[str, object]]) -> str:
    for item in artwork:
        if item["id"] == DEFAULT_ART_ID:
            return str(item["file"])
    raise ValueError(f"default artwork ID {DEFAULT_ART_ID} is absent from manifest")


def kitty_config() -> str:
    return "\n".join((
        "# Generated from assets/art/fata-morgana/manifest.json by",
        "# tools/build_art_selectors.py.  The glob makes every approved JPEG",
        "# available to Kitty without an external picker or a hidden script.",
        "background_image ${HOME}/.local/share/fata-morgana/art/*.jpg",
        "background_image_layout cscaled",
        "background_image_linear yes",
        "background_tint 0.60",
        "background_tint_gaps 1.0",
        "",
    ))


def rofi_theme() -> str:
    return "\n".join((
        "/* Generated from assets/art/fata-morgana/manifest.json by",
        " * tools/build_art_selectors.py.  scripts/fata-rofi supplies",
        " * FM_ROFI_ART as a complete, validated Rasi image value. */",
        "* {",
        "    fm-rofi-art: env(FM_ROFI_ART, linear-gradient(to bottom, #2C2D2E, #202023));",
        "}",
        "",
    ))


def rofi_launcher(filenames: list[str], default: str) -> str:
    allowed = "|\n        ".join(f'"{filename}"' for filename in filenames)
    return f"""#!/bin/sh
# Generated from assets/art/fata-morgana/manifest.json by
# tools/build_art_selectors.py.
# Runtime dependencies: a POSIX-compatible /bin/sh and rofi with Wayland
# support.  No directory scan or external text-processing utility is used.
set -eu

fm_rofi_art_file=${{FM_ROFI_ART_FILE:-{default}}}
case "$fm_rofi_art_file" in
        {allowed}) ;;
    *)
        printf '%s\\n' "fata-rofi: FM_ROFI_ART_FILE is not in the approved Fata Morgana catalogue" >&2
        exit 64
        ;;
esac

fm_rofi_mode=${{FM_ROFI_MODE:-drun}}
case "$fm_rofi_mode" in
    drun|run|window) ;;
    *)
        printf '%s\\n' "fata-rofi: FM_ROFI_MODE must be drun, run, or window" >&2
        exit 64
        ;;
esac

if [ -z "${{HOME:-}}" ]; then
    printf '%s\\n' "fata-rofi: HOME is required to locate installed artwork" >&2
    exit 64
fi

FM_ROFI_ART="url(\\\"{DATA_ART_DIR}/${{fm_rofi_art_file}}\\\", height)"
export FM_ROFI_ART
exec rofi -show "$fm_rofi_mode" "$@"
"""


def main() -> None:
    artwork = load_artwork()
    filenames = sorted(str(item["file"]) for item in artwork)
    default = default_filename(artwork)

    outputs = {
        KITTY_ART_PATH: kitty_config(),
        ROFI_ART_PATH: rofi_theme(),
        ROFI_LAUNCHER_PATH: rofi_launcher(filenames, default),
    }
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
