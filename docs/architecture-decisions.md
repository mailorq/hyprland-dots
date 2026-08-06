# Architecture decisions

Baseline date: 2026-08-04.

## Compatibility baseline

- Target Hyprland 0.55 or newer and use `hyprland.lua`. Hyprlang `.conf`
  compositor configuration is not part of the new implementation.
- Keep application-specific palette adapters valid for their real parsers:
  Hyprland Lua, GTK 3 CSS, Rasi, and kitty config syntax.
- Use only declared runtime or asset-build dependencies. The art-master build
  requires the explicitly pinned Pillow range in `tools/requirements-assets.txt`;
  component-specific exports will add no implicit tools.

## Hardware and layout profile

- Primary target: 27-inch 2560×1440 monitor.
- Secondary target: 23-inch monitor; its output name and native resolution are
  intentionally not hard-coded before hardware detection.
- Geometry is expressed in logical pixels and remains usable at 1920×1080.
- Default Hyprland geometry: `gaps_in = 8`, `gaps_out = 12`, `border_size = 2`,
  and `rounding = 8`.
- Default Waybar geometry: 40 px bar height, 32 px module height, 8 px top
  margin, 12 px horizontal margins, 10 px module horizontal padding, and 6 px
  inter-module spacing.
- Provide 10 numbered workspaces. Actual monitor assignment remains a local
  override because connector names cannot be safely inferred from this repo.

## Desktop and laptop profiles

- The default installation profile is `desktop`.
- The desktop Waybar must not contain battery, backlight, power-profile, or
  temperature modules.
- The installer offers explicit battery, backlight, and combined laptop
  profiles. Temperature remains a separate opt-in rather than an implicit
  laptop default.
- Profile-specific Waybar JSONC files must not call absent helper utilities.

## Pointer input

- The physical mouse is configured for 1200 DPI.
- DPI alone is not enough to derive a Hyprland sensitivity value. Keep neutral
  compositor sensitivity until the user chooses acceleration (`flat` or
  adaptive) and reports the desired pointer feel in Phase 3.

## Visual and asset policy

- The theme is medium-dark and overcast, not black-heavy: graphite and storm
  gray surfaces, muted bone text, restrained burgundy, and aged brass accents.
- Only the user-provided Fata Morgana reference allowlist may produce committed
  artwork. No image, logo, character, or decorative element from another title
  in `hateme-dots` may be imported.
- Artwork roles are non-exclusive. Any approved Fata Morgana reference may be
  reused in Kitty, Rofi, notifications, the lock screen, or another focused UI
  surface; an image selected as a desktop wallpaper remains eligible for those
  same surfaces.
- Each integration receives its own size and crop export from the same source.
  Portrait images are not excluded from the visual system merely because they
  are unsuitable for a 16:9 desktop wallpaper.
- Base wallpapers may use only native 16:9 references or compositions that
  tolerate a small, deliberate crop to 16:9. Wallpaper exports must not use
  blurred side-fill, framed portrait layouts, subject distortion, or generative
  fill.
- Hyprpaper is the declared static wallpaper backend. It starts once with the
  session, uses one fallback image across unknown outputs, and has no automatic
  slideshow, preloading, or helper script.

## Documentation references

- Hyprland configuration start page: <https://wiki.hypr.land/Configuring/Start/>
- Hyprland variables: <https://wiki.hypr.land/Configuring/Basics/Variables/>
- GTK 3 CSS overview: <https://docs.gtk.org/gtk3/css-overview.html>
- Rofi theme format: <https://davatorium.github.io/rofi/current/rofi-theme.5/>
- Kitty configuration: <https://sw.kovidgoyal.net/kitty/conf/>
- Hyprpaper configuration: <https://wiki.hypr.land/Hypr-Ecosystem/hyprpaper/>
