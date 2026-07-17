# -*- coding: utf-8 -*-
user = env["res.users"].browse(85)
UserPub = env["hr.employee.public"].with_user(user)
r44 = UserPub.browse(44)
m = env["hr.employee.access.mixin"]
print("user id", r44.env.user.id)
print("refs via user arg", m._hr_employee_access_reference_readable_ids(user))
print("refs via env.user", m._hr_employee_access_reference_readable_ids(r44.env.user))
print("filter", r44._hr_employee_filter_accessible().ids)
