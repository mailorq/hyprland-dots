-- Generic, portable fallback. Explicit local monitor rules loaded from
-- fata/local.lua take precedence for the actual QHD and secondary outputs.
hl.monitor({
    output = "",
    mode = "preferred",
    position = "auto",
    scale = "auto",
})
