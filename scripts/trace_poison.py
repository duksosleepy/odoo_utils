# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
user = env["res.users"].browse(85)
mixin = env["hr.employee.access.mixin"]
UserPub = env["hr.employee.public"].with_user(user)

def show(label):
    own = user.sudo().employee_id
    print(label, "org", mixin._hr_employee_access_org_reference_readable_ids(user),
          "parent", own.parent_id.id)

show("before")
r44 = UserPub.browse(44)
show("after browse 44")
r44._hr_employee_filter_accessible()
show("after filter 44")
r44._hr_employee_read_is_restricted()
show("after restricted check")
r44.read(["name"])
show("after read 44")
