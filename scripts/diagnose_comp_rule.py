# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u = env["res.users"].browse(85)
# poison cache like restricted check
UserPub = env["hr.employee.public"].with_user(u)
UserPub.browse(81)._hr_employee_read_is_restricted()

own = u.employee_id
print("after restricted: parent_id", own.parent_id.id)

rule = env.ref("hr.hr_employee_public_comp_rule")
domain = rule._compute_domain("hr.employee.public", "read", u)
print("comp rule domain", domain)

e44 = env["hr.employee.public"].browse(44)
ok = e44.sudo().filtered_domain(domain)
print("e44 passes comp_rule", bool(ok))

try:
    UserPub.browse(44).check_access("read")
    print("check_access 44 OK")
except Exception as e:
    print("check_access 44 FAIL", str(e)[:150])
