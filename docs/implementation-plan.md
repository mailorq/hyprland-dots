# Fata Morgana dots — implementation plan

This repository is built in narrow, verifiable stages. A later stage cannot
silently change a completed contract from an earlier one.

## 1. Foundation and source audit — complete

**Purpose:** establish the target architecture before any runnable dotfile is
written.

**Outputs**

- `docs/source-audit-hateme-dots.md`: evidence-based list of patterns that are
  useful only as visual inspiration and must not be copied.
- `docs/dependency-contract.md`: component ownership, profile rules, and
  validation commands.
- A stable repository map:

  ```text
  assets/       approved visual sources and generated, role-specific exports
  config/       installable XDG configuration trees
  docs/         architecture, audits, and operational notes
  scripts/      explicit runtime helpers only
  tests/        static and runtime validation helpers
  theme/        canonical palette and per-application adapters
  ```

**Exit gate**

- Hyprland baseline, XDG layout, profiles, dependencies, validation criteria,
  and non-goals are documented.
- No legacy Hyprlang configuration, copied upstream artwork, or hidden runtime
  helper is introduced.

## 2. Artwork catalogue and palette — complete

**Purpose:** turn the reference set into reusable visual assets and freeze the
Fata Morgana semantic palette.

**Work**

- Reconcile the currently changing `pictures/` staging folder, give each
  accepted image a stable, ASCII-safe catalogue name, record source metadata,
  and preserve the original separately from exports.
- Assign non-exclusive roles: an image may appear in Kitty, Rofi, Mako or the
  lock screen as well as in the wallpaper set.
- Select only composition-safe native or lightly cropped 16:9 sources for
  desktop wallpaper exports. Do not apply this limitation to other UI uses.
- Resample the palette from the frozen set, validate contrast, and generate
  `theme/colors.lua`, `theme/colors.css`, `theme/colors.rasi`, and the
  Kitty-compatible `theme/colors.conf` from one canonical source.

**Exit gate**

- Every export has a purpose, original source, dimensions, and reproducible
  generation rule.
- Palette adapters are byte-for-byte synchronized with the canonical tokens.

## 3. Hyprland compositor — baseline ready for runtime validation; personal binds pending

**Purpose:** create a current Hyprland 0.55+ Lua configuration for the desktop
workflow.

**Work**

- Build `config/hypr/hyprland.lua` and small Lua modules using the current
  `hl.config`, `hl.monitor`, `hl.bind`, and `hl.window_rule` APIs.
- Add a 10-workspace desktop workflow, QHD-first but FHD-safe logical geometry,
  and a local, Git-ignored monitor override for real output names.
- Integrate the user's supplied keybindings only after they are provided;
  never fabricate or silently replace them.
- Configure mouse behavior after the user chooses flat or adaptive
  acceleration; 1200 DPI alone is not a compositor sensitivity value.

**Exit gate**

- Lua parses and Hyprland reloads without errors on the target Linux system.
- No legacy `source =`, `windowrule =`, `animation =`, or deprecated
  `decoration:drop_shadow` syntax remains.

## 4. Kitty, Rofi, and Mako — in progress

**Purpose:** apply the mansion visual system to focused interaction surfaces.

**Work**

- Kitty: readable QHD/FHD typography, restrained transparency, and optional
  per-window background image selection from the shared asset catalogue.
- Rofi: valid Rasi theme, keyboard-first layout, image treatment that does not
  obscure search results, and `rofi -rasi-validate` validation.
- Mako: compact notification geometry, urgency states, source-aware icons, and
  no dependency on an unavailable Dunst-specific feature.

**Exit gate**

- Kitty parses its config, Rofi validates its Rasi files, and Mako starts with
  the selected configuration on Wayland.

## 5. Waybar, profiles, integration, and final QA — in progress

**Purpose:** build the final desktop panel and installation profile selection.

**Work**

- Build a clean desktop Waybar: launcher, 10 workspaces, focused title,
  clock, audio, network, and tray. No battery, temperature, brightness,
  power-profile, CPU, or memory monitoring on the desktop profile.
- Provide explicit `laptop-battery`, `laptop-backlight`, and
  `laptop-battery-backlight` variants. Temperature is separately opt-in and
  never inferred from laptop selection.
- Add a dependency preflight and an installation workflow with dry-run support;
  do not use blanket copies such as `cp -r /* ~/`.
- Validate on the QHD primary display and a FHD-compatible secondary display,
  then inspect stderr and application logs for parser errors.

**Exit gate**

- All selected components load without stderr parser errors.
- Every called binary is declared, checked, and either mandatory or clearly
  opt-in.
- The final self-audit is clean and the user receives commit-sized file groups.

## Required checkpoint protocol

At the end of each stage:

1. Answer whether there are bugs, missing context, unverified assumptions, or
   documentation conflicts.
2. Trace relationships between findings; state whether one could cause another.
3. Correct every fixable issue before presenting the result.
4. Provide only proposed commit groups: exact files and a commit message. The
   user reviews, stages, and commits them.

