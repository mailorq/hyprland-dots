# Fata Morgana wallpapers

`fata-morgana/` is generated only by `tools/build_wallpapers.py` from the five
masters marked as wallpaper-eligible in `assets/art/fata-morgana/manifest.json`.
Every export has an exact 16:9 crop, retains its source pixels without upscale,
and has a manifest-recorded source checksum and crop box.

The default fallback is `fm-016`: it has the highest source resolution of the
approved set, a calm dark-right area for window contrast, and an intentionally
restrained burgundy/light focus. The other four exports are selectable assets,
not an automatic slideshow.
