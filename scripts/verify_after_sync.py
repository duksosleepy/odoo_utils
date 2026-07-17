import json
u = env["res.users"].browse(57)
u._sync_lug_odoo_groups()
u = env["res.users"].browse(57)
out = {
    "groups": [(g.id, g.full_name) for g in u.group_ids],
    "leaves": env["hr.leave"].with_user(57).search([]).mapped(lambda l: (l.id, l.employee_id.name, l.employee_id.ma_bo_phan_id.name if l.employee_id.ma_bo_phan_id else None)),
    "employees": env["hr.employee"].with_user(57).search([]).mapped(lambda e: (e.id, e.name, e.ma_bo_phan_id.name if e.ma_bo_phan_id else None)),
    "can_open_emp4": bool(env["hr.employee"].with_user(57).search([("id", "=", 4)])),
}
with open(r"D:\Lap_odoo\lug_debug_after_sync.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=str)
