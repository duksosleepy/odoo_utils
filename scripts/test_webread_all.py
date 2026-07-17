# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
user = env["res.users"].browse(85)
UserPub = env["hr.employee.public"].with_user(user)
r44 = UserPub.browse(44)
r81 = UserPub.browse(81)
# Simulate form open: restricted check runs before reads
print("restricted", r81._hr_employee_read_is_restricted())
print("filter 44", r44._hr_employee_filter_accessible().ids)
print("read 44", r44.read(["name"]))
try:
    data = r81.web_read({"parent_id": {"fields": {"display_name": {}}}})
    print("web_read 81 OK", data[0].get("parent_id"))
except Exception as e:
    print("web_read 81 FAIL", type(e).__name__, repr(str(e)[:120]))
