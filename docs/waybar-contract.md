# Waybar profile and geometry contract

Waybar is structured as a small generated profile family, not as one copied
monolithic `config.jsonc`. `tools/build_waybar_profiles.py` emits strict JSON
with a `.jsonc` suffix; therefore both Waybar and the static validator can read
the same files without a non-standard comment parser.

## Profile matrix

| Profile | Optional hardware cells | Intentionally absent |
|---|---|---|
| `desktop` | none | battery, backlight, temperature, power profile, CPU, memory |
| `laptop-battery` | battery | backlight, temperature, power profile, CPU, memory |
| `laptop-backlight` | backlight | battery, temperature, power profile, CPU, memory |
| `laptop-battery-backlight` | battery and backlight | temperature, power profile, CPU, memory |

The later installation workflow must make the profile choice explicit and
install exactly one generated file as Waybar's active `config.jsonc`. It must
not infer a laptop from the presence of a sysfs path. Temperature has no
profile: it needs a separately approved source and dependency before it can be
represented.

All profiles share only the daily desktop cells: static `MENU` launcher, ten
Hyprland workspaces, per-output focused title, centered clock, volume, network
state, and tray. `MENU` invokes only the already-declared `fata-rofi` helper;
the custom module has static text and no polling `exec` process. Volume and
brightness use their native Waybar module behaviours, not hidden `wpctl`,
`pactl`, or `brightnessctl` scripts.

## Geometry

The panel preserves the same compact coordinate system as the compositor:

| Value | CSS/config value | Result |
|---|---:|---|
| Bar height | 40 px | The bar remains proportionate on QHD and FHD. |
| Top/outer horizontal margins | 8 / 12 px | QHD usable width: 2536 px; FHD: 1896 px. |
| Cell track | 32 px | 40 px bar minus 4 px vertical margin above and below. |
| Inter-cell gap | 6 px | Adjacent cells each provide 3 px lateral margin. |
| Cell border / rounding | 2 px / 8 px | Matches Hyprland focus frames without oversized pills. |
| Cell interior padding | 10 px | Keeps labels readable without wasting horizontal space. |
| Workspace buttons | 22 px minimum, 7 px lateral padding | Ten numbered workspaces remain compact and directly targetable. |
| Focused-title floor | 240 px | Prevents a one-character title from collapsing the left panel. |

With a 240 px title floor, a ten-workspace group of roughly 250 px, and the
short text-only status cells, the layout stays well inside 1920 px. The title
is capped at 46 characters, and `fixed-center` prevents its expansion from
shifting the clock. The panel uses generic `serif` rather than a downloaded
font, so the subdued mansion character has no undeclared font dependency.

The visual language is deliberately cell-based: each functional group has its
own rounded card, while the ten workspace buttons sit inside one compact card.
The active workspace is burgundy with a brass edge; urgency uses the existing
danger token. There are no transitions, shadows, CSS variables, vendor-prefixed
GTK declarations, or icon-font requirements.

## Workspace semantics

`config/hypr/fata/workspaces.lua` declares workspaces 1–10 persistent. The
Waybar profile mirrors that through `persistent-workspaces: { "*": 10 }` and
shows only persistent workspaces, sorted numerically. The current monitor gets
the target when a workspace button is clicked (`move-to-monitor: true`), while
scrolling the module is disabled to avoid accidental workspace changes.

Waybar's documented persistent-workspace support still needs both sides of this
contract: generated Waybar configuration and loaded Hyprland persistent rules.
The actual Waybar/Hyprland version pair must be checked on Linux by clicking a
workspace on each output; this is a runtime compatibility check, not a reason
to add an undocumented dispatcher script.

## Validation gate

Regenerate and check the source tree first:

```sh
python3 tools/build_theme_colors.py
python3 tools/build_waybar_profiles.py
python3 tools/validate_waybar_static.py
```

Then, inside the target Wayland session, test the selected profile and inspect
all stderr output:

```sh
waybar --config config/waybar/config.desktop.jsonc --style config/waybar/style.css
```

Repeat with the intended laptop variant, if one is selected. Confirm no GTK CSS
warnings occur, workspace click targets operate on both displays, and the
desktop profile exposes no hardware-monitoring cell. Windows cannot execute
this final parser and compositor gate.

## Source references

- [Waybar Hyprland workspace module](https://github.com/Alexays/Waybar/blob/master/man/waybar-hyprland-workspaces.5.scd)
- [Waybar custom module](https://github.com/Alexays/Waybar/blob/master/man/waybar-custom.5.scd)
- [Waybar PulseAudio module](https://github.com/Alexays/Waybar/blob/master/man/waybar-pulseaudio.5.scd)
- [Waybar network module](https://github.com/Alexays/Waybar/blob/master/man/waybar-network.5.scd)
- [Waybar battery module](https://github.com/Alexays/Waybar/blob/master/man/waybar-battery.5.scd)
- [Waybar backlight module](https://github.com/Alexays/Waybar/blob/master/man/waybar-backlight.5.scd)
