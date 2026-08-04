-- 1200 DPI is a hardware setting, not a Hyprland sensitivity value. Keep the
-- compositor neutral and let libinput select its device default until the user
-- explicitly chooses flat or adaptive acceleration in fata/local.lua.
hl.config({
    input = {
        sensitivity = 0.0,
        accel_profile = "",
    },
})

hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")
