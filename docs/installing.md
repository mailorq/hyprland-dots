# Installation and preflight

`scripts/fata-install` deploys only files owned by this repository. Invoke the
tracked source with `sh scripts/fata-install`; the installed `fata-rofi` helper
is made executable by the deployment. The installer is a
POSIX shell helper, not a distribution installer: it never invokes a package
manager, starts a daemon, chooses a laptop profile automatically, or removes
an existing configuration directory.

## Before deployment

The active graphical session needs `Hyprland`, `kitty`, Wayland-capable `rofi`,
`mako`, and a Waybar build with Hyprland, PulseAudio, network, and tray
modules. The deployment writes `fata-rofi` to `~/.local/bin`, and the `MENU`
cell plus `Super+F` invoke that exact HOME-relative path. They therefore do not
depend on the display manager inheriting `~/.local/bin` in `PATH`.

Choose the hardware profile deliberately:

| Profile | Use when |
|---|---|
| `desktop` | normal PC install; no hardware-monitoring cells |
| `laptop-battery` | a laptop needs only its battery cell |
| `laptop-backlight` | a laptop needs only the native display-brightness cell |
| `laptop-battery-backlight` | both optional laptop cells are desired |

Temperature, power profile, CPU, and memory are not install options. The
installer verifies `/sys/class/power_supply/BAT*` or `/sys/class/backlight/*`
only after the respective laptop profile was requested; it never uses these
paths to choose a profile on the user's behalf.

The artwork path is intentionally fixed at `~/.local/share/fata-morgana/art/`
because Kitty and `fata-rofi` use that same explicit HOME-relative location.
Configuration files use `XDG_CONFIG_HOME` when it is set, otherwise
`~/.config`.

## Safe workflow

From the repository root, inspect the exact plan first:

```sh
sh scripts/fata-install --profile desktop
```

After installing the required packages, run the non-mutating dependency check:

```sh
sh scripts/fata-install --profile desktop --check
```

Deploy only after both checks are understood:

```sh
sh scripts/fata-install --profile desktop --apply
```

If a managed destination file already exists, the deployment stops before it
writes anything. Review the difference yourself; only then, if replacing that
exact managed file is intended, repeat with `--force`:

```sh
sh scripts/fata-install --profile desktop --apply --force
```

`--force` can replace only the named files in the plan. It refuses to write
through a destination symbolic link and never deletes files or directories.
Local Hyprland and Kitty overrides remain untouched.

After deployment, the next Hyprland start launches only Mako and Waybar. A
plain `hyprctl reload` intentionally does not create a second instance of
either process.

## Post-install runtime gate

Run these commands inside the target Wayland session and inspect stderr:

```sh
fm_config_home=${XDG_CONFIG_HOME:-"$HOME/.config"}
hyprctl reload
rofi -rasi-validate "$fm_config_home/rofi/config.rasi"
kitty --config "$fm_config_home/kitty/kitty.conf" --debug-config
mako --config "$fm_config_home/mako/config"
waybar --config "$fm_config_home/waybar/config.jsonc" --style "$fm_config_home/waybar/style.css"
```

Verify all ten workspace buttons on both monitors, the `MENU` cell, and the
absence of battery, backlight, temperature, CPU, memory, and power-profile
cells in the `desktop` profile. These are target-system checks; they cannot be
proven from Windows. Run the Mako and Waybar commands when an instance of the
same daemon is not already owned by the current session; they are parser and
stderr tests, not services to leave duplicated in the background.
