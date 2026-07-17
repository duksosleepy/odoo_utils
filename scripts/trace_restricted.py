# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
user = env["res.users"].browse(85)
m = env["hr.employee.access.mixin"]
UserPub = env["hr.employee.public"].with_user(user)
r44 = UserPub.browse(44)

def refs(label):
    own = user.sudo().employee_id
    print(label, m._hr_employee_access_org_reference_readable_ids(user), own.parent_id.id)

refs("1")
print("restricted", r44._hr_employee_read_is_restricted())
refs("2 after restricted")
print("enforced", user.sudo()._lug_permission_is_enforced())
refs("3 after enforced")
