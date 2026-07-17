import json
user = env["res.users"].browse(57)
user._sync_lug_odoo_groups()
user = env["res.users"].browse(57).with_user(57)
hidden = user._lug_hidden_menu_ids()
menus = env["ir.ui.menu"].sudo().browse(hidden)
out = {
    "perm": {k: list(v) for k, v in user._lug_effective_permission_map().items()},
    "hidden_count": len(hidden),
    "hidden_roots": [m.name for m in menus if not m.parent_id],
    "groups": [g.full_name for g in env["res.users"].browse(57).group_ids],
}
with open(r"D:\Lap_odoo\lug_debug_fix.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
