# -*- coding: utf-8 -*-
u = env["res.users"].sudo().browse(85)
emp44 = env["hr.employee"].sudo().browse(44)
print("user emp", u.employee_id.id, u.employee_id.name.encode("unicode_escape").decode())
print("emp44 dept", emp44.department_id.id, "parent", emp44.parent_id.id if emp44.parent_id else None)
print("emp44 user", emp44.user_id.id if emp44.user_id else None)

UserEmp = env["hr.employee"].with_user(u)
UserPub = env["hr.employee.public"].with_user(u)

print("employee search count", UserEmp.search_count([]))
print("public search count", UserPub.search_count([]))
print("employee 44 in search", bool(UserEmp.search([("id", "=", 44)])))
print("public 44 in search", bool(UserPub.search([("id", "=", 44)])))

data = UserEmp.search_read([("id", "=", 44)], ["name", "department_id", "parent_id"])
print("employee search_read", data)

data2 = UserPub.search_read([("id", "=", 44)], ["name", "department_id"])
print("public search_read", data2)

mixin = env["hr.employee.access.mixin"]
domain = mixin._hr_employee_visibility_read_domain(u, model_name="hr.employee.public")
print("public visibility domain", domain)

domain2 = mixin._hr_employee_visibility_read_domain(u, model_name="hr.employee")
print("employee visibility domain", domain2)
