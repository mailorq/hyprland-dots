-- User-approved base bindings live in one auditable module.  The map keeps the
-- Super/Win vocabulary familiar without reserving application-specific helpers
-- or undeclared command dependencies.

local fata_rofi = '"$HOME/.local/bin/fata-rofi"'
-- The installed launcher path does not depend on a display manager inheriting
-- ~/.local/bin in PATH. / Путь к лаунчеру не зависит от PATH графической сессии.

hl.bind("SUPER + Q", hl.dsp.exec_cmd("kitty"))
-- Launch Kitty. / Запустить Kitty.

hl.bind("SUPER + Tab", hl.dsp.focus({ last = true }))
-- Toggle focus to the last window, like a compact Alt+Tab. / Перейти к последнему окну, как компактный Alt+Tab.

hl.bind("SUPER + F", hl.dsp.exec_cmd(fata_rofi))
-- Open the Fata Morgana Rofi launcher. / Открыть лаунчер Rofi в стиле Fata Morgana.

hl.bind("SUPER + SHIFT + C", hl.dsp.window.close({}))
-- Request graceful close of the focused window. / Корректно закрыть активное окно.

hl.bind("SUPER + Space", hl.dsp.window.float({ action = "toggle" }))
-- Toggle floating for the focused window. / Переключить плавающий режим активного окна.

hl.bind("SUPER + M", hl.dsp.window.fullscreen({ action = "toggle", mode = "fullscreen" }))
-- Toggle fullscreen for the focused window. / Переключить полноэкранный режим активного окна.

local workspace_keys = {
    { key = "1", id = 1 },
    { key = "2", id = 2 },
    { key = "3", id = 3 },
    { key = "4", id = 4 },
    { key = "5", id = 5 },
    { key = "6", id = 6 },
    { key = "7", id = 7 },
    { key = "8", id = 8 },
    { key = "9", id = 9 },
    { key = "0", id = 10 },
}

for _, item in ipairs(workspace_keys) do
    hl.bind("SUPER + " .. item.key, hl.dsp.focus({ workspace = item.id, on_current_monitor = true }))
    -- Focus numbered workspace on the current monitor. / Перейти на рабочее пространство текущего монитора.

    hl.bind("SUPER + SHIFT + " .. item.key, hl.dsp.window.move({ workspace = item.id }))
    -- Move focused window to numbered workspace. / Перенести активное окно на рабочее пространство.
end
