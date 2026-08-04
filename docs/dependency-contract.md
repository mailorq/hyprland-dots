# Dependency and profile contract

The project names a binary only when the component that invokes it owns that
dependency. A feature is either mandatory, optional through a profile, or not
implemented. Silent fallbacks are prohibited.

## Baseline runtime

| Component | Mandatory binary | Scope | Notes |
|---|---|---|---|
| Compositor | `Hyprland` 0.55+ | all profiles | Lua configuration only. |
| Terminal | `kitty` | all profiles | Reads a Kitty-valid colour include and the approved-art glob. |
| Launcher | `rofi` with Wayland support | all profiles | Rasi is validated before release; `fata-rofi` uses only POSIX `sh` plus this binary. |
| Notifications | `mako` | all profiles | Native Mako config; Dunst is not a hidden substitute. |
| Panel | `waybar` | all profiles | Requires the Hyprland, PulseAudio, network, and tray modules enabled in the packaged build. |

The exact distribution packages are intentionally not listed yet: package names
vary by distribution, and the user has not selected a target distribution.

## Optional features

| Feature | Required binary/service | Selected by |
|---|---|---|
| Wallpaper management | One chosen backend, preflight required | wallpaper stage |
| Clipboard history | `wl-paste`, `wl-copy`, and `cliphist` | only if its binds are requested |
| Audio display and scroll control | Waybar PulseAudio module plus PulseAudio or PipeWire-Pulse service | every current Waybar profile |
| Launcher cell | `fata-rofi` helper on `PATH` | every current Waybar profile |
| Laptop battery | Waybar native battery module and `/sys/class/power_supply/` data | explicitly selected battery profile only |
| Laptop backlight | Waybar native backlight module and a udev-visible backlight device | explicitly selected backlight profile only |
| CPU/GPU temperature | explicitly chosen backend | separate opt-in only |

## Profile contract

- `desktop` is the default: no battery, backlight, temperature, power-profile,
  CPU, or memory module.
- `laptop-battery`, `laptop-backlight`, and `laptop-battery-backlight` are
  deliberate installation choices. They never auto-detect hardware or modify
  the desktop profile.
- Temperature is absent from all currently generated profiles. Adding it later
  requires a separately selected backend and a separate dependency declaration.
- Local hardware facts such as connector names, refresh rates, device names,
  and GPU-specific environment variables live in Git-ignored local overrides.
- A missing optional dependency hides no errors: the relevant profile is not
  installed until its preflight passes.

## Validation contract

| Surface | Required check before handoff |
|---|---|
| Lua | Static Lua parse where available, then `hyprctl reload` on the target system. |
| Hyprland | Inspect reload output and `hyprctl monitors all` / `hyprctl devices` against local overrides. |
| Rofi | `rofi -rasi-validate` for every Rasi file. |
| Kitty | Launch a controlled Kitty instance with the intended `--config` path and inspect stderr; use Kitty's `debug_config` action for runtime diagnostics. |
| Mako | Start using the intended config and inspect stderr on a Wayland session. |
| Waybar | Start each selected generated profile with explicit config/style paths and inspect stderr for JSON or GTK CSS diagnostics. |
| Scripts | `shellcheck` when a shell helper exists; every external command is preflighted. |

## Source references

- [Hyprland Lua configuration](https://wiki.hypr.land/Configuring/Start/)
- [Rofi theme syntax](https://davatorium.github.io/rofi/current/rofi-theme.5/)
- [Kitty configuration](https://sw.kovidgoyal.net/kitty/conf/)
- [Mako configuration](https://www.mankier.com/5/mako)
- [Waybar Hyprland workspace module](https://github.com/Alexays/Waybar/blob/master/man/waybar-hyprland-workspaces.5.scd)
- [Waybar custom module](https://github.com/Alexays/Waybar/blob/master/man/waybar-custom.5.scd)
