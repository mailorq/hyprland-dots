#!/bin/sh
# Exercise fata-install against an isolated temporary home directory.
# This test never invokes Hyprland or changes a real user configuration.
set -eu

PATH=/usr/bin:/bin
export PATH

fm_test_root=$(mktemp -d)
fm_test_script_dir=$(CDPATH= cd -P "$(dirname "$0")" && pwd)
fm_test_repo=$(CDPATH= cd -P "$fm_test_script_dir/.." && pwd)

fm_test_cleanup() {
    # mktemp created this directory in this process; no user path is removed.
    rm -rf "$fm_test_root"
}

trap 'fm_test_cleanup' 0
trap 'fm_test_cleanup; exit 128' 1 2 15

fm_test_bin="$fm_test_root/bin"
fm_test_home="$fm_test_root/home"
fm_test_config="$fm_test_root/config"
mkdir -p "$fm_test_bin" "$fm_test_home" "$fm_test_config"

for fm_test_command in Hyprland hyprpaper kitty btop rofi mako waybar; do
    printf '%s\n' '#!/bin/sh' 'exit 0' > "$fm_test_bin/$fm_test_command"
    chmod 0755 "$fm_test_bin/$fm_test_command"
done

PATH="$fm_test_bin:$PATH"
HOME="$fm_test_home"
XDG_CONFIG_HOME="$fm_test_config"
export PATH HOME XDG_CONFIG_HOME

sh "$fm_test_repo/scripts/fata-install" --profile desktop --apply >/dev/null

[ -f "$XDG_CONFIG_HOME/hypr/hyprland.lua" ]
[ -x "$HOME/.local/bin/fata-rofi" ]
[ -f "$HOME/.local/share/fata-morgana/art/fata-morgana-001-red-masked-portrait.jpg" ]
[ -f "$HOME/.local/share/fata-morgana/wallpapers/fata-morgana-016-violet-cloaked-portrait-wallpaper-16x9.jpg" ]
[ ! -d "$HOME/.local/state/fata-morgana/backups" ]

if sh "$fm_test_repo/scripts/fata-install" --profile desktop --apply >/dev/null 2>&1; then
    printf '%s\n' 'install integration: expected managed-file conflict did not occur' >&2
    exit 1
fi

printf '%s\n' 'locally-modified-before-force' > "$XDG_CONFIG_HOME/hypr/fata/input.lua"
sh "$fm_test_repo/scripts/fata-install" --profile desktop --apply --force >/dev/null
set -- "$HOME/.local/state/fata-morgana/backups"/*
[ -d "$1" ]
[ -f "$1/config/hypr/hyprland.lua" ]
[ -f "$1/bin/fata-rofi" ]
sh "$fm_test_repo/scripts/fata-install" --restore "$1" >/dev/null
[ "$(cat "$XDG_CONFIG_HOME/hypr/fata/input.lua")" = 'locally-modified-before-force' ]

printf '%s\n' 'Install integration: pass'
