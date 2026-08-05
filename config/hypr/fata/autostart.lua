-- Start only the session services owned by this dotfile set.  The
-- hyprland.start event runs once per compositor start, so a config reload does
-- not spawn duplicates.  hl.exec_cmd() is already asynchronous: no shell
-- backgrounding or process-detection helper is required.
hl.on("hyprland.start", function()
    hl.exec_cmd("mako")
    hl.exec_cmd("waybar")
end)
