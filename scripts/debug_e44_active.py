# -*- coding: utf-8 -*-
e44 = env["hr.employee"].sudo().browse(44)
p44 = env["hr.employee.public"].sudo().browse(44)
print("emp active", e44.active, "exists", e44.exists())
print("pub active", p44.active if p44.exists() else None, "exists", p44.exists())
print("pub sudo read", p44.read(["name", "active"]))

u = env["res.users"].sudo().browse(85)
refs = env["hr.employee.access.mixin"]._hr_employee_access_reference_readable_ids(u)
print("refs", refs)
own = u.employee_id
print("own parent", own.parent_id.id)

UserPub = env["hr.employee.public"].with_user(u)
print("search 44", UserPub.search([("id", "=", 44)]).ids)
print("search active false", UserPub.with_context(active_test=False).search([("id", "=", 44)]).ids)
