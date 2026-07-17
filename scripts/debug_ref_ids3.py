# -*- coding: utf-8 -*-
u = env["res.users"].sudo().browse(85)
mixin = env["hr.employee.access.mixin"]
refs = mixin._hr_employee_access_reference_readable_ids(u)
print("ref ids", refs)

UserPub = env["hr.employee.public"].with_user(u)
r = UserPub.browse(44)
print("restricted", r._hr_employee_read_is_restricted())
allowed = r._hr_employee_filter_accessible()
print("filter ids", allowed.ids)
print("read", allowed.read(["name"]))

r81 = UserPub.browse(81)
print("e81 parent web_read", r81.web_read({"parent_id": {"fields": {"display_name": {}}}}))
