# -*- coding: utf-8 -*-
u = env["res.users"].sudo().browse(85)
mixin = env["hr.employee.access.mixin"]
refs = mixin._hr_employee_access_reference_readable_ids(u)
print("ref ids", refs, "44 in refs", 44 in refs)

UserPub = env["hr.employee.public"].with_user(u)
r = UserPub.browse(44)
print("filter accessible ids", r._hr_employee_filter_accessible().ids)
try:
    print("web_read", r.web_read({"name": {}}))
except Exception as e:
    print("web_read FAIL", type(e).__name__)
