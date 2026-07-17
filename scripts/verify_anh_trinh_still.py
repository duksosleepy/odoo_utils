# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
u = env["res.users"].browse(85)
print("anh.trinh policy", env["hr.employee.access.mixin"]._hr_employee_policy_domain(u))
Pub = env["hr.employee.public"].with_user(u)
print("VP", Pub.search_count([("mien", "=", "VP")]), "Nam", Pub.search_count([("mien", "=", "Nam")]))
Pub.browse(81)._hr_employee_read_is_restricted()
try:
    Pub.browse(44).check_access("read")
    print("parent 44 OK")
    Pub.browse(81).web_read({"parent_id": {"fields": {"display_name": {}}}})
    print("own form OK")
except Exception as ex:
    print("FAIL", str(ex)[:150])
