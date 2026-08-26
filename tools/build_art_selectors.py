"""Generate application-side artwork selectors from the approved manifest.

The generated Rofi launcher intentionally uses only POSIX ``sh`` and the
mandatory ``rofi`` binary at runtime.  It does not scan directories or invoke
random-selection utilities: the manifest is the allowlist.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "assets" / "art" / "fata-morgana" / "manifest.json"
MASTER_DIR = MANIFEST_PATH.parent
KITTY_ART_PATH = ROOT / "config" / "kitty" / "fata" / "art.conf"
ROFI_ART_PATH = ROOT / "config" / "rofi" / "fata" / "art.rasi"
ROFI_LAUNCHER_PATH = ROOT / "scripts" / "fata-rofi"
DATA_ART_DIR = "${HOME}/.local/share/fata-morgana/art"
DEFAULT_ART_ID = "fm-038"
ARTWORK_ID_PATTERN = re.compile(r"fm-[0-9]{3}")
ARTWORK_FILENAME_PATTERN = re.compile(
    r"fata-morgana-(?P<index>[0-9]{3})-[a-z0-9]+(?:-[a-z0-9]+)*\.jpg"
)


def validate_artwork_filename(filename: object) -> str:
    if not isinstance(filename, str) or not ARTWORK_FILENAME_PATTERN.fullmatch(filename):
        raise ValueError(f"invalid generated artwork filename: {filename!r}")
    return filename


def validate_artwork(artwork: object) -> list[dict[str, object]]:
    if not isinstance(artwork, list) or not artwork:
        raise ValueError("art manifest contains no artwork")

    filenames: set[str] = set()
    ids: set[str] = set()
    for item in artwork:
        if not isinstance(item, dict):
            raise ValueError("art manifest contains a non-object artwork entry")
        artwork_id = item.get("id")
        if not isinstance(artwork_id, str) or not ARTWORK_ID_PATTERN.fullmatch(artwork_id):
            raise ValueError(f"invalid artwork ID: {artwork_id!r}")
        roles = item.get("roles", [])
        filename = validate_artwork_filename(item.get("file"))
        filename_match = ARTWORK_FILENAME_PATTERN.fullmatch(filename)
        assert filename_match is not None
        if artwork_id != f"fm-{filename_match.group('index')}":
            raise ValueError(f"artwork ID and filename index differ: {artwork_id} / {filename}")
        if artwork_id in ids:
            raise ValueError(f"duplicate artwork ID: {artwork_id}")
        if filename in filenames:
            raise ValueError(f"duplicate generated artwork filename: {filename}")
        if roles != ["kitty", "rofi"]:
            raise ValueError(f"{artwork_id} must target exactly Kitty and Rofi")
        master = MASTER_DIR / filename
        if not master.is_file() or master.is_symlink():
            raise ValueError(f"approved artwork master is missing or not regular: {filename}")
        ids.add(artwork_id)
        filenames.add(filename)
    return artwork


def load_artwork() -> list[dict[str, object]]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise ValueError("art manifest schema must be version 1")
    return validate_artwork(manifest.get("artwork"))


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
    approved = [validate_artwork_filename(filename) for filename in filenames]
    if not approved:
        raise ValueError("cannot generate a launcher without approved artwork")
    if default not in approved:
        raise ValueError("the default artwork must be in the approved catalogue")
    allowed = "|\\\n        ".join(f'"{filename}"' for filename in approved)
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
        with path.open("w", encoding="utf-8", newline="\n") as output:
            output.write(content)


if __name__ == "__main__":
    main()
