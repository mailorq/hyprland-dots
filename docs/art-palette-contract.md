# Art and palette contract

The generated reference set contains 40 user-supplied Fata Morgana images. The raw
`pictures/` directory is ignored and remains unchanged; the committed master
collection is generated through a SHA-256 allowlist rather than source names.
This prevents an accidental replacement or a foreign-title image from quietly
becoming part of the theme.

## Rebuild and validation

```text
python -m pip install -r tools/requirements-assets.txt
python tools/build_theme_colors.py
python tools/build_art_assets.py
python tools/build_art_assets.py --check
```

`build_art_assets.py` creates 2048 px-or-smaller sRGB masters with clean
English filenames. It corrects EXIF orientation and removes metadata but never
crops or enlarges an illustration. Every master remains eligible for Kitty,
Rofi, Mako, and lockscreen use. A shared-surface portrait cannot exceed a
height-to-width ratio of 1.60: this retains `fm-026` at 1.555 while excluding
vertical-16:9 compositions that would lose too much content in Kitty and Rofi.

Five masters have reproducible 16:9 desktop-wallpaper exports with either
native framing or a centered crop that removes at most 21.9% of the source
area. The exports retain the masters' original pixel density and never upscale:

| Asset | Treatment |
|---|---|
| `fm-016` | centered crop, 20.9% loss |
| `fm-031` | centered crop, 19.5% loss |
| `fm-035` | centered crop, 20.4% loss |
| `fm-038` | native 16:9 |
| `fm-040` | centered crop, 20.6% loss |

`tools/build_wallpapers.py` emits the five exact crops and a second manifest to
`assets/wallpapers/fata-morgana/`. The default is `fm-016`, which has the
highest source resolution and deliberate dark right-side negative space; the
other four are available but never rotate automatically. The build uses only
the already approved candidates from the art manifest: it cannot promote the
remaining 35 images to wallpapers.

## Palette

`theme/palette.json` is the only color source. The four adapters are generated
from it: `colors.css` for GTK 3/Waybar, `colors.rasi` for Rofi,
`colors.conf` for Kitty, and `colors.lua` for Hyprland Lua.

| Token | Hex | Use |
|---|---|---|
| `bg` | `#2C2D2E` | medium-dark overcast base |
| `surface` | `#3C3B3B` | panel and elevated surface |
| `surface_warm` | `#493B36` | restrained warm depth |
| `fg` | `#E9E1D7` | primary bone text |
| `fg_dim` | `#92949A` | secondary text, AA against `bg` |
| `burgundy` | `#5F2F28` | gothic accent, not body text |
| `brass` | `#B39A6A` | focused accent, AA against `bg` |
| `storm` | `#8E9BA8` | cold overcast counterpoint |

The verified contrast ratios are 10.66:1 for `fg` on `bg`, 4.55:1 for
`fg_dim` on `bg`, and 5.09:1 for `brass` on `bg`.
