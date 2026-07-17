# -*- coding: utf-8 -*-
user = env["res.users"].browse(85)
UserPub = env["hr.employee.public"].with_user(user)
r44 = UserPub.browse(44)
r81 = UserPub.browse(81)
print("refs", env["hr.employee.access.mixin"]._hr_employee_access_reference_readable_ids(user))
print("filter 44", r44._hr_employee_filter_accessible().ids)
print("read 44", r44.read(["name"]))
try:
    print("web_read 81", r81.web_read({"parent_id": {"fields": {"display_name": {}}}}))
except Exception as e:
    print("web_read FAIL", type(e).__name__)
