# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

u = env["res.users"].browse(85)
print("holidays_user", u.has_group("hr_holidays.group_hr_holidays_user"))
print("leave_mien_vp", u.has_group("hr_leave_type_mien.group_leave_mien_vp"))
leaves = env["hr.leave"].with_user(u).search([])
print("leave count", len(leaves), "miens", leaves.mapped("employee_leave_mien"))
lv41 = env["hr.leave"].with_user(u).browse(41)
print("can read leave 41", lv41.exists())
try:
    data = lv41.web_read({"employee_id": {"fields": {"display_name": {}}}})
    print("web_read leave 41 employee", data[0].get("employee_id"))
except Exception as ex:
    print("web_read FAIL", ex)

Pub = env["hr.employee.public"].with_user(u)
print("VP visible", Pub.search_count([("mien", "=", "VP")]))
print("Nam visible", Pub.search_count([("mien", "=", "Nam")]))
