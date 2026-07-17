import json
user = env["res.users"].browse(57).with_user(57)
hidden = user._lug_hidden_menu_ids()
perm = {k: list(v) for k, v in user._lug_effective_permission_map().items()}
menus = env["ir.ui.menu"].sudo().browse(hidden)
out = {
    "hidden": hidden,
    "perm": perm,
    "enforced": user._lug_permission_is_enforced(),
    "hidden_names": [m.complete_name for m in menus],
    "groups": [(g.id, g.full_name) for g in env["res.users"].browse(57).group_ids],
}
with open(r"D:\Lap_odoo\lug_debug2.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
