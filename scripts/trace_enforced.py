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

refs("before enforced")
print("enforced", user.sudo()._lug_permission_is_enforced())
refs("after enforced")
