# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
u = env["res.users"].browse(58)
UserPub = env["hr.employee.public"].with_user(u)
mixin = env["hr.employee.access.mixin"]
domain = mixin._hr_employee_visibility_read_domain(u, model_name="hr.employee.public")
print("domain", domain)

for e in env["hr.employee"].sudo().search([("mien", "=", "Nam")]):
    vis = bool(UserPub.search([("id", "=", e.id)], limit=1))
    print(e.id, e.name, "visible", vis, "dept", e.department_id.id, "leave_mgr", e.leave_manager_id.id)
