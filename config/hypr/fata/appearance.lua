local colors = require("fata.colors")

-- Logical-pixel geometry is deliberately compact on QHD and remains balanced
-- on FHD: 8 px inner gaps, 12 px outer gaps, a 2 px focus border, and 8 px
-- rounding. The panel's exclusive zone is configured by Waybar in Phase 5.
hl.config({
    general = {
        gaps_in = 8,
        gaps_out = 12,
        gaps_workspaces = 0,
        border_size = 2,
        resize_on_border = false,
        allow_tearing = false,
        layout = "dwindle",
        col = {
            active_border = colors.brass,
            inactive_border = colors.border,
        },
    },
    decoration = {
        rounding = 8,
        rounding_power = 3,
        active_opacity = 1.0,
        inactive_opacity = 1.0,
        fullscreen_opacity = 1.0,
        dim_inactive = false,
        shadow = {
            enabled = false,
        },
        blur = {
            enabled = false,
        },
        glow = {
            enabled = false,
        },
        motion_blur = {
            enabled = false,
        },
        wobble = {
            enabled = false,
        },
    },
    dwindle = {
        preserve_split = true,
    },
    misc = {
        force_default_wallpaper = 0,
        disable_hyprland_logo = true,
        disable_splash_rendering = true,
        background_color = colors.bg_deep,
    },
})

-- One calm enter curve and no perpetual angle animation. Window movement stays
-- responsive, while workspace changes use only a short, low-distance fade.
hl.curve("fm_ease_out", {
    type = "bezier",
    points = { { 0.22, 1.0 }, { 0.36, 1.0 } },
})

hl.animation({ leaf = "global",     enabled = true, speed = 2.4, bezier = "fm_ease_out" })
hl.animation({ leaf = "windows",    enabled = true, speed = 2.6, bezier = "fm_ease_out" })
hl.animation({ leaf = "windowsIn",  enabled = true, speed = 2.6, bezier = "fm_ease_out", style = "popin 94%" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 1.6, bezier = "fm_ease_out", style = "popin 94%" })
hl.animation({ leaf = "fade",       enabled = true, speed = 1.8, bezier = "fm_ease_out" })
hl.animation({ leaf = "layers",     enabled = true, speed = 1.8, bezier = "fm_ease_out", style = "fade" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 2.2, bezier = "fm_ease_out", style = "slidefade 8%" })
