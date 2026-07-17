import json
u = env["res.users"].browse(57)
u._sync_lug_visibility_policy()
u._sync_lug_odoo_groups()
u = env["res.users"].browse(57)
user = u.with_user(57)
hidden = user._lug_hidden_menu_ids()
menus = env["ir.ui.menu"].sudo().browse(hidden)
hr_menus = env["ir.ui.menu"].sudo().search([
    ("parent_id", "=", env.ref("hr.menu_hr_root").id)
])
out = {
    "lug_data_scope": u.lug_data_scope,
    "visibility_policy": u.visibility_policy,
    "assigned_ma_bo_phan": u.assigned_ma_bo_phan_ids.mapped("name"),
    "systray": user._lug_ui_systray_flags(),
    "hidden_hr_submenus": [
        m.name for m in menus
        if m.parent_id and m.parent_id.id == env.ref("hr.menu_hr_root").id
    ],
    "visible_hr_submenus": [m.name for m in hr_menus if m.id not in hidden],
    "employee_count": env["hr.employee"].with_user(57).search_count([]),
}
with open(r"D:\Lap_odoo\lug_debug_phuong.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
