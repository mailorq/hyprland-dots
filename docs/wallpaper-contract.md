# Wallpaper and Hyprpaper contract

## Scope

The wallpaper layer uses only the official `hyprpaper` backend and the five
images already marked `wallpaper.eligible` in
`assets/art/fata-morgana/manifest.json`. It is intentionally static: no
wallpaper randomizer, transition daemon, timer, directory scan at runtime, or
third-party title can appear in the running session.

`tools/build_wallpapers.py` produces the exact 16:9 crops in
`assets/wallpapers/fata-morgana/`. It reads committed masters and their
manifest, never the ignored `pictures/` directory. The generated manifest
records the source checksum, final checksum, exact crop box, crop loss, and the
one default choice.

## Curated set

| ID | Output dimensions | Crop loss | Default | Reason |
|---|---:|---:|---|---|
| `fm-016` | 2048×1152 | 20.9% | yes | Highest detail; muted burgundy with dark right-side field for windows. |
| `fm-031` | 736×414 | 19.5% | no | Quiet grayscale scene; selectable, not forced. |
| `fm-035` | 736×414 | 20.4% | no | Focused light shaft; selectable, not forced. |
| `fm-038` | 736×414 | 0.0% | no | Native 16:9 moonlit scene; selectable, not forced. |
| `fm-040` | 1456×819 | 21.9% | no | Forest and blue-butterfly counterpoint; selectable, not forced. |

No export is enlarged. QHD displays may scale a smaller original according to
the compositor/backend, but the repository never fabricates pixels or applies
an artificial sharpening pass. This is preferable to silently creating a fake
"2K" image from a small source.

## Runtime configuration

`config/hypr/hyprpaper.conf` uses the current documented Hyprpaper parser, not
Hyprland Lua. It sets `splash = false`, keeps IPC available for inspection, and
declares an unnamed-monitor fallback with `fit_mode = cover`. The unnamed rule
works for the user's unknown QHD and secondary output names without assuming
connector strings.

Hyprpaper's current documented config lookup is
`~/.config/hypr/hyprpaper.conf`. The installer deliberately writes that one
file there even when `XDG_CONFIG_HOME` is custom; all other supported component
configs still use `XDG_CONFIG_HOME` as described in the installation guide.

The Hyprland session hook starts exactly one `hyprpaper` process. A config
reload does not relaunch it. Old online snippets with `preload`, `reload`,
`unload`, or `listloaded` are prohibited: current upstream documentation says
to inspect the installed version's supported requests instead.

This repository owns that startup through `fata/autostart.lua`. Do not also
enable `hyprpaper.service` through UWSM or the user systemd manager: the
service is an alternative ownership model, not an additional launch method.
If startup ownership is moved to such a service in a future local setup,
remove the matching autostart command only as one reviewed, documented change.

## Validation

From the repository root, regenerate and verify before deployment:

```sh
python3 tools/build_art_assets.py
python3 tools/build_wallpapers.py
python3 tools/build_wallpapers.py --check
python3 tools/validate_wallpapers_static.py
```

After installation, inside the running Wayland session:

```sh
hyprctl hyprpaper listactive
```

The output must list the deployed `fm-016` wallpaper for every monitor that
does not have a deliberately configured local override. Inspect Hyprpaper's
stderr at session start; do not add a second `hyprpaper` process just to test
it.

## Source reference

- [Current Hyprpaper documentation](https://wiki.hypr.land/Hypr-Ecosystem/hyprpaper/)
