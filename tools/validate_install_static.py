"""Verify the installation helper's safety and routing contract."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "fata-install"


def fail(message: str) -> None:
    raise SystemExit(f"Install static contract: FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> None:
    text = INSTALLER.read_text(encoding="utf-8")
    require(text.startswith("#!/bin/sh\n"), "installer must use POSIX sh")
    require("set -eu" in text, "installer must fail on unset variables and command errors")
    require("fm_mode=dry-run" in text, "installer must default to dry-run")
    require("--force requires --apply" in text, "force must require explicit apply mode")
    require("--restore requires a backup directory" in text,
            "installer must require an explicit backup directory for restore")
    require("XDG_CONFIG_HOME must be an absolute path" in text,
            "installer must not write through a relative XDG_CONFIG_HOME")
    require("fm_has_symlink_in_target_path" in text and "refusing to write through symbolic link in target path" in text,
            "installer must reject a destination symlink or a symlinked ancestor")
    require("refusing to replace managed files without --force" in text,
            "installer must reject existing managed files by default")
    require(text.count('rm -f "$fm_temp"') == 1,
            "installer may only remove its resolved mktemp file during cleanup")
    require("rm -rf" not in text and "rm -r " not in text and "rm -R " not in text,
            "installer must not recursively delete files or directories")
    require("cp -r" not in text and "cp -R" not in text,
            "installer must not recursively copy an unspecified directory")

    for profile in (
        "desktop",
        "laptop-battery",
        "laptop-backlight",
        "laptop-battery-backlight",
    ):
        require(profile in text, f"installer lacks explicit {profile} profile")
    for fragment in (
        "fm_require_command Hyprland",
        "fm_require_command hyprpaper",
        "fm_require_command kitty",
        "fm_require_command rofi",
        "fm_require_command mako",
        "fm_require_command waybar",
        "fm_has_battery || fm_die",
        "fm_has_display_backlight || fm_die",
        "fm_verify_release",
        "sha256sum -c \"assets/deployment.sha256\"",
        "required source file must not be a symbolic link",
        "fm_map_action=validate",
        "mktemp \"$fm_target_dir/.fata-install.XXXXXX\"",
        "mv -f \"$fm_temp\" \"$fm_publish_target\"",
        "backups/$(date -u +%Y%m%dT%H%M%SZ)-$$",
        "targets.tsv",
        "fm_validate_restore_dir",
        "fm_publish_file",
        "restored $fm_restored_count managed file(s)",
        "Hyprland reloads the entry point as it is saved. Publish it last",
        "appearance autostart bindings colors input monitors workspaces",
        "config/hypr/hyprpaper.conf",
        "config.$fm_profile.jsonc",
        "fata-rofi",
        "assets/art/fata-morgana/*.jpg",
        "assets/wallpapers/fata-morgana/*.jpg",
    ):
        require(fragment in text, f"installer lacks required route or preflight: {fragment!r}")

    print("Install static contract: pass")


if __name__ == "__main__":
    main()
