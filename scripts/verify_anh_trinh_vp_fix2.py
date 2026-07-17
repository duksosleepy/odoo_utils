# -*- coding: utf-8 -*-
u = env["res.users"].browse(85)
u._sync_lug_odoo_groups()
print("after sync holidays_user", u.has_group("hr_holidays.group_hr_holidays_user"))
lv = env["hr.leave"].with_user(u).browse(41)
print("leave in search", bool(env["hr.leave"].with_user(u).search([("id", "=", 41)])))
try:
    print(lv.web_read({"employee_id": {"fields": {"display_name": {}}}}))
except Exception as ex:
    print("web_read err", type(ex).__name__, ex)
# VP leaves in db?
vp_leaves = env["hr.leave"].sudo().search([("employee_leave_mien", "=", "VP")])
print("vp leaves total", len(vp_leaves))
print("vp leaves visible", env["hr.leave"].with_user(u).search([("employee_leave_mien", "=", "VP")]))
