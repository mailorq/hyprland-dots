"""Low-risk structural checks for the Hyprland 0.55+ Lua tree.

This is deliberately not a replacement for `hyprctl reload` on Linux. It catches
regressions that can be checked without Hyprland or a Lua interpreter: deprecated
Hyprlang declarations, missing required modules, palette drift, and fabricated
binds before the user supplies them.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HYPR_DIR = ROOT / "config" / "hypr"
ENTRYPOINT = HYPR_DIR / "hyprland.lua"
OPTIONAL_MODULES = {"fata.local"}
LEGACY_PATTERNS = {
    "Hyprlang source declaration": re.compile(r"^\s*source\s*=", re.MULTILINE),
    "legacy windowrule declaration": re.compile(r"^\s*windowrule\w*\s*=", re.MULTILINE),
    "legacy animation declaration": re.compile(r"^\s*animation\s*=", re.MULTILINE),
    "legacy drop-shadow namespace": re.compile(r"decoration:drop_shadow"),
}
REQUIRE_PATTERN = re.compile(r'require\(\s*["\']([A-Za-z0-9_./-]+)["\']\s*\)')


def module_path(module: str) -> Path:
    return HYPR_DIR / (module.replace(".", "/") + ".lua")


def main() -> int:
    errors: list[str] = []
    lua_files = sorted(HYPR_DIR.rglob("*.lua"))
    if ENTRYPOINT not in lua_files:
        errors.append("missing config/hypr/hyprland.lua")

    for path in lua_files:
        content = path.read_text(encoding="utf-8")
        for description, pattern in LEGACY_PATTERNS.items():
            if pattern.search(content):
                errors.append(f"{description}: {path.relative_to(ROOT)}")

        for module in REQUIRE_PATTERN.findall(content):
            if module not in OPTIONAL_MODULES and not module_path(module).is_file():
                errors.append(f"missing required module {module!r} referenced by {path.relative_to(ROOT)}")

    colors = HYPR_DIR / "fata" / "colors.lua"
    canonical_colors = ROOT / "theme" / "colors.lua"
    if not colors.is_file() or colors.read_bytes() != canonical_colors.read_bytes():
        errors.append("config/hypr/fata/colors.lua is not synchronized with theme/colors.lua")

    bindings = HYPR_DIR / "fata" / "bindings.lua"
    if not bindings.is_file():
        errors.append("missing base bindings module")
    else:
        binding_text = bindings.read_text(encoding="utf-8")
        for fragment in (
            'hl.bind("SUPER + Q", hl.dsp.exec_cmd("kitty"))',
            'hl.bind("SUPER + Tab", hl.dsp.focus({ last = true }))',
            'local fata_rofi = \'"$HOME/.local/bin/fata-rofi"\'',
            'hl.bind("SUPER + F", hl.dsp.exec_cmd(fata_rofi))',
            'hl.bind("SUPER + SHIFT + C", hl.dsp.window.close({}))',
            'hl.bind("SUPER + Space", hl.dsp.window.float({ action = "toggle" }))',
            'hl.bind("SUPER + M", hl.dsp.window.fullscreen({ action = "toggle", mode = "fullscreen" }))',
            '{ key = "0", id = 10 },',
            'hl.dsp.focus({ workspace = item.id, on_current_monitor = true })',
            'hl.dsp.window.move({ workspace = item.id })',
        ):
            if fragment not in binding_text:
                errors.append(f"base binding contract lacks {fragment}")
        if re.search(r'hl\.dsp\.exec_(?:cmd|raw)\("(?!kitty"\))', binding_text):
            errors.append("bindings.lua invokes an undeclared external command")

    workspace_file = HYPR_DIR / "fata" / "workspaces.lua"
    if not workspace_file.is_file() or "for workspace = 1, 10 do" not in workspace_file.read_text(encoding="utf-8"):
        errors.append("the ten-workspace contract is absent")

    autostart_file = HYPR_DIR / "fata" / "autostart.lua"
    if not autostart_file.is_file():
        errors.append("missing Fata session autostart module")
    else:
        autostart = autostart_file.read_text(encoding="utf-8")
        for fragment in ('hl.on("hyprland.start"', 'hl.exec_cmd("mako")', 'hl.exec_cmd("waybar")'):
            if fragment not in autostart:
                errors.append(f"autostart lacks {fragment}")
        if "&" in autostart:
            errors.append("autostart must not shell-background session services")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Hyprland static contract: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
