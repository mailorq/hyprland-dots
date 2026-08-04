# Kitty, Rofi and Mako contract

This stage styles three focused interaction surfaces without inventing a
window-manager binding or a hardware monitor.

## Artwork routing

The approved manifest is the only artwork allowlist.
`tools/build_art_selectors.py` requires every entry to carry both `kitty` and
`rofi` roles; it currently generates selectors for all 40 masters. It does not
inspect `pictures/` or any unapproved file at runtime.

- Kitty receives a native JPEG glob at
  `${HOME}/.local/share/fata-morgana/art/*.jpg`. Kitty documents this as a
  native multi-image background source; it keeps additional images on demand.
  `cscaled` retains the artwork aspect ratio, so a portrait is never stretched
  just to fill a terminal. The `0.60` tint keeps a shell readable while
  retaining the image's silhouette.
- `scripts/fata-rofi` selects any approved filename through
  `FM_ROFI_ART_FILE`. Its default is the native 16:9
  `fata-morgana-038-moonlit-sleep.jpg`; an explicit filename selects any other
  approved master. The shell code has only two runtime dependencies: POSIX
  `/bin/sh` and the mandatory Wayland-capable `rofi` binary. It does not call
  `find`, `shuf`, `sed`, Python, or a wallpaper daemon.
- Mako has no native arbitrary background-image feature. It keeps source
  application icons enabled and uses its own supported color, radius and
  urgency options; no Dunst-specific feature or GTK CSS is emulated.

The installation stage must deploy normalized masters to
`~/.local/share/fata-morgana/art/`, configurations to their XDG directories,
and optionally make `scripts/fata-rofi` available as `fata-rofi`. Mako's single
generated config has no include path, so it remains valid when a user chooses a
non-default `XDG_CONFIG_HOME`. Until that stage, the source tree is intentionally
not copied into a live home directory.

## Geometry

| Surface | FHD-safe baseline | QHD adjustment | Reasoning |
|---|---:|---:|---|
| Kitty | 12 pt text, 10 pt interior padding | same point sizes | Point units preserve readable terminal density across common 96 to 144 DPI setups; the compositor owns the outer 2 px frame. |
| Rofi | 42% monitor width, 7 rows, 16 px shell padding | 38% width and 9 rows when output width is at least 2200 px | FHD: about 806 px wide; QHD: about 973 px wide. The 16:9 reference art scaled to launcher height remains close to the usable panel width rather than being stretched. |
| Mako | 380 px maximum width, 160 px maximum height, 3 visible | same | At 1920 px, a notification is under one fifth of screen width; at 2560 px it remains compact. 8 px outer + 4 px notification margin places the first card 12 px from an edge. |

Rofi uses only Rasi selectors and documented widget properties. Its semi-opaque
inner rows preserve text contrast even for a bright approved frame. Mako's high
urgency state is persistent (`default-timeout=0`) and uses the palette's
danger/burgundy pair; low urgency is cool storm, normal is brass.

## Linux validation gate

Run the static checks after generators, then validate parsers on the actual
Wayland host:

```sh
python3 tools/build_theme_colors.py
python3 tools/build_art_selectors.py
python3 tools/validate_interaction_static.py
rofi -rasi-validate ~/.config/rofi/config.rasi
kitty --config ~/.config/kitty/kitty.conf --debug-config
mako --config ~/.config/mako/config
```

The final Mako command must be started inside a Wayland session and its stderr
inspected. It is a startup test, not a second notification daemon to leave
running. Windows cannot execute this gate; it remains mandatory before the
stage is marked complete.

## Source references

- [Kitty configuration](https://sw.kovidgoyal.net/kitty/conf/)
- [Rofi Rasi theme syntax](https://davatorium.github.io/rofi/current/rofi-theme.5/)
- [Mako configuration](https://man.archlinux.org/man/mako.5)
