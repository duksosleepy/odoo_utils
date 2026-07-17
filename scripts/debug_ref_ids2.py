# -*- coding: utf-8 -*-
u = env["res.users"].sudo().browse(85)
UserPub = env["hr.employee.public"].with_user(u)
r = UserPub.browse(44)
allowed = r._hr_employee_filter_accessible()
print("allowed", allowed.ids)
try:
    print("read name", allowed.read(["name"]))
except Exception as e:
    print("read FAIL", type(e).__name__, str(e)[:100].encode("unicode_escape").decode())

try:
    ac = allowed._check_access("read")
    print("check_access", ac)
except Exception as e:
    print("_check_access FAIL", type(e).__name__)

try:
    fa = allowed._filtered_access("read")
    print("filtered_access", fa.ids)
except Exception as e:
    print("_filtered_access FAIL", type(e).__name__)
