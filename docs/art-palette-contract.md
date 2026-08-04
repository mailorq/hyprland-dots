# Art and palette contract

The generated reference set contains 41 user-supplied Fata Morgana images. The raw
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
Rofi, Mako, and lockscreen use.

Five masters may later become QHD 16:9 desktop wallpapers with either native
framing or a centered crop that removes at most 20.9% of the source area:

| Asset | Treatment |
|---|---|
| `fm-016` | centered crop, 20.9% loss |
| `fm-031` | centered crop, 19.5% loss |
| `fm-035` | centered crop, 20.4% loss |
| `fm-038` | native 16:9 |
| `fm-040` | centered crop, 20.6% loss |

No desktop wallpaper export is generated in this phase. That avoids repeating
the rejected all-images-as-wallpapers approach, while keeping every image
available to the application surfaces where portrait composition is useful.

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
