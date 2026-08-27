-- Generic, portable fallback. An integer scale keeps the QHD/FHD geometry
-- deterministic and avoids an unsolicited fractional scale. Explicit local
-- monitor rules take precedence whenever a different scale is intentional.
hl.monitor({
    output = "",
    mode = "preferred",
    position = "auto",
    scale = 1,
})
