# Hyprland contract

The compositor target is Hyprland 0.55 or newer. Its entrypoint is
`$XDG_CONFIG_HOME/hypr/hyprland.lua`; no `hyprland.conf`, `source =`, legacy
`windowrule =`, legacy `animation =`, or `decoration:drop_shadow` is used.

## Portable geometry

| Token | Value | QHD 2560x1440 result | FHD 1920x1080 result |
|---|---:|---:|---:|
| `gaps_in` | 8 px | two tiled columns: 1264 px each | 944 px each |
| `gaps_out` | 12 px | stable 12 px perimeter | stable 12 px perimeter |
| `border_size` | 2 px | visible focus edge without bulk | same logical thickness |
| `rounding` | 8 px | restrained, not pill-shaped | restrained, not pill-shaped |

The two-column widths above derive from `(screen width - 2 * gaps_out -
gaps_in) / 2`. Waybar will reserve its own top-layer space in Phase 5, so the
compositor does not guess its exclusive zone.

## Display, workspace, and input policy

- The portable monitor rule uses each display's preferred mode, automatic
  position, and automatic scale. Real connector names, placement, and refresh
  rates belong in the ignored `fata/local.lua`, copied from `local.lua.example`.
- Workspaces 1–10 are persistent. They are intentionally not preassigned to a
  monitor until the user supplies actual output names and desired split.
- Mouse sensitivity stays at `0.0`; empty `accel_profile` preserves libinput's
  device default. 1200 DPI alone does not justify a guessed curve.
- `fata/bindings.lua` provides a deliberately small Super/Win baseline: Kitty,
  Rofi, last-window focus, close, floating, fullscreen, and workspace 1–10.
  `Super+Tab` is the Alt+Tab analogue and focuses the previously active window;
  it does not pretend to be a workspace switcher. The only commands named by
  bindings are mandatory `kitty` and the installed `fata-rofi` helper. The
  Rofi bind uses the helper's exact HOME-relative deployment path so it does
  not depend on a display manager propagating `~/.local/bin` into PATH.

## Motion and decoration

Window, layer, and workspace motion share one short Bézier curve. There are no
border-angle loops, opacity dimming, blur, glow, wobble, or shadow effects in
the baseline. The active border uses aged brass and the inactive border uses the
muted structural token from the canonical palette.

## Session services

`fata/autostart.lua` listens only for `hyprland.start` and launches `mako` plus
`waybar` through `hl.exec_cmd()`. It does not launch a wallpaper daemon, a
hardware monitor, a tray applet, a shell wrapper, or a duplicate process on
config reload. Both called binaries are mandatory and preflighted by the
installation helper.

## Validation

Run `python tools/validate_hyprland_static.py` after editing the config tree.
On the Linux target, then run `hyprctl reload`, inspect its output, and capture
`hyprctl monitors all` plus `hyprctl devices` before writing `fata/local.lua`.
