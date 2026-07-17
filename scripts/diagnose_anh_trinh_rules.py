# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

u = env["res.users"].browse(85)
print("groups:", [g.name for g in u.group_ids.sorted("name")])
print("has holidays responsible", u.has_group("hr_holidays.group_hr_holidays_responsible"))
print("has holidays user", u.has_group("hr_holidays.group_hr_holidays_user"))
print("has holidays manager", u.has_group("hr_holidays.group_hr_holidays_manager"))
print("leave mien vp", u.has_group("hr_leave_type_mien.group_leave_mien_vp"))
print("leave mien store", u.has_group("hr_leave_type_mien.group_leave_mien_store"))

for lv_id in [41, 42, 43, 44, 40]:
    lv = env["hr.leave"].sudo().browse(lv_id)
    print(f"\nleave {lv_id} emp {lv.employee_id.id} mien {lv.employee_leave_mien}")
    for rule in env["ir.rule"].with_user(u)._get_rules("hr.leave", "read"):
        dom = rule._compute_domain("hr.leave", "read")
        match = env["hr.leave"].sudo().browse(lv_id).filtered_domain(dom)
        if match:
            print("  matched rule", rule.id, rule.name[:60])

# Why employee fetch fails on overview
lv = env["hr.leave"].with_user(u).browse(41)
try:
    data = lv.web_read({"employee_id": {"fields": {"display_name": {}}}})
    print("\nweb_read employee_id", data)
except Exception as ex:
    print("\nweb_read FAIL", type(ex).__name__, ex)
