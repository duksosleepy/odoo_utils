# -*- coding: utf-8 -*-
u = env["res.users"].sudo().browse(85)
UserPub = env["hr.employee.public"].with_user(u)
r = UserPub.browse(44)
print("filter", r._hr_employee_filter_accessible().ids)
print("filtered_access", r._filtered_access("read").ids)
print("exists", r.exists())
try:
    r.check_access("read")
    print("check_access OK")
except Exception as e:
    print("check_access", type(e).__name__)

# try with bypass
r2 = UserPub.browse(44).with_context(bypass_access=True)
print("bypass read", r2.read(["name"]))

# name_get
try:
    print("name_get", r.name_get())
except Exception as e:
    print("name_get FAIL", type(e).__name__)
