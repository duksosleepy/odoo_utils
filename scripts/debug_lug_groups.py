import json
u = env["res.users"].browse(57)
managed = u._lug_managed_group_ids()
target = u._lug_target_group_ids()
out = {
    "managed_count": len(managed),
    "target": [(g.id, g.full_name) for g in env["res.groups"].browse(list(target))],
    "current": [(g.id, g.full_name, g.id in managed) for g in u.group_ids],
    "keep": [(g.id, g.full_name) for g in u.group_ids.filtered(lambda g: g.id not in managed)],
}
u._sync_lug_odoo_groups()
u = env["res.users"].browse(57)
out["after"] = [(g.id, g.full_name) for g in u.group_ids]
with open(r"D:\Lap_odoo\lug_debug_groups.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
