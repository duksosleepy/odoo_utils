import json
out = []
users = env["res.users"].search([("login", "ilike", "phuong")])
for u in users:
    info = {
        "id": u.id,
        "login": u.login,
        "lug_group_ids": u.lug_group_ids.ids,
        "enforced": u._lug_permission_is_enforced(),
        "perm_map": {k: list(v) for k, v in u._lug_effective_permission_map().items()},
        "hidden_menus": u._lug_hidden_menu_ids(),
        "group_ids": u.group_ids.ids,
    }
    out.append(info)
for g in env["lug.group"].search([]):
    out.append({
        "group_id": g.id,
        "group_name": g.name,
        "users": g.user_ids.ids,
        "permissions": [
            {
                "app": line.app_id.code,
                "menu_xmlid": line.app_id.menu_xmlid,
                "perms": list(line._active_permission_codes()),
            }
            for line in g.permission_line_ids
        ],
    })
apps = env["lug.app"].search([])
out.append({
    "apps": [
        {"code": a.code, "menu_xmlid": a.menu_xmlid, "menu_ids": a._resolve_menu_ids()}
        for a in apps
    ]
})
with open(r"D:\Lap_odoo\lug_debug.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
