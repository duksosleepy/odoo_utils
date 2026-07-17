# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
user = env["res.users"].browse(85)
mixin = env["hr.employee.access.mixin"]
UserPub = env["hr.employee.public"].with_user(user)
r44 = UserPub.browse(44)
print("restricted", r44._hr_employee_read_is_restricted())
print("org refs", mixin._hr_employee_access_org_reference_readable_ids(user))
