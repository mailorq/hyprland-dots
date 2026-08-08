-- Keep ten numbered workspaces alive. They are intentionally not bound to a
-- physical output here: monitor assignment belongs in the user-local override
-- after `hyprctl monitors all` identifies the real connector names.
for workspace = 1, 10 do
    hl.workspace_rule({
        workspace = tostring(workspace),
        persistent = true,
    })
end
