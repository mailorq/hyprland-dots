-- Fata Morgana desktop configuration for Hyprland 0.55+.
-- Hyprland evaluates each require() in an isolated scope, keeping the
-- ownership of configuration failures narrow and their diagnostics visible.

require("fata.monitors")
require("fata.appearance")
require("fata.input")
require("fata.workspaces")
require("fata.bindings")
require("fata.autostart")

-- The tracked example documents local monitor, keyboard, and pointer overrides.
-- A real `fata/local.lua` is optional and deliberately ignored by Git. Missing
-- local overrides are normal; any other load error must stay visible.
local local_ok, local_error = pcall(require, "fata.local")
if not local_ok then
    local missing_local_module = type(local_error) == "string"
        and local_error:match("^module 'fata%.local' not found")
    if not missing_local_module then
        error(local_error)
    end
end
