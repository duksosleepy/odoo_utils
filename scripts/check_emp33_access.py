# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
u85 = env["res.users"].browse(85)
Pub = env["hr.employee.public"].with_user(u85)
r33 = Pub.browse(33)
print("filter 33", r33._hr_employee_filter_accessible().ids)
print("restricted", r33._hr_employee_read_is_restricted())
try:
    r33.check_access("read")
    print("check_access 33 OK")
except Exception as ex:
    print("check_access 33 FAIL", ex)
result = r33._check_access("read")
print("_check_access returns", result)
