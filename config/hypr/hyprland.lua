-- Fata Morgana desktop configuration for Hyprland 0.55+.
-- Relative require() modules are isolated by Hyprland, so an error in one
-- module does not stop the unaffected configuration modules from loading.

require("fata.monitors")
require("fata.appearance")
require("fata.input")
require("fata.workspaces")
require("fata.bindings")
require("fata.autostart")

-- The tracked example documents local monitor, keyboard, and pointer overrides.
-- A real `fata/local.lua` is optional and deliberately ignored by Git. Missing
-- local overrides are normal; any other load error must stay visible.
local local_ok, local_result = pcall(require, "fata.local")
if not local_ok and not tostring(local_result):find("not found", 1, true) then
    error(local_result)
end
