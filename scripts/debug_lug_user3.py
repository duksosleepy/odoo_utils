import json
u = env["res.users"].browse(57)
out = {
    "user_role": u.user_role,
    "visibility_policy": u.visibility_policy,
    "lug_groups": [(g.id, g.name) for g in u.lug_group_ids],
    "extra_perms": [(l.app_id.code, list(l._active_permission_codes())) for l in u.lug_user_permission_ids],
    "group_lines": [
        (l.app_id.code, list(l._active_permission_codes()))
        for g in u.lug_group_ids for l in g.permission_line_ids
    ],
    "roots": env["ir.ui.menu"].sudo().search([("parent_id", "=", False)]).read(["id", "name", "complete_name"]),
}
with open(r"D:\Lap_odoo\lug_debug3.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
