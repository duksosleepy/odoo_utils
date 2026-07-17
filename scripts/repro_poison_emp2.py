# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
Pub = env["hr.employee.public"].with_user(u85)
Emp = env["hr.employee"].with_user(u85)

# poison like opening employees menu
Pub.browse(81)._hr_employee_read_is_restricted()
own_parent = u85.employee_id.parent_id.id
print("own parent after poison", own_parent)

for eid in [2, 52, 44, 8]:
    try:
        Pub.browse(eid).check_access("read")
        print(f"public {eid} check_access OK")
    except Exception as ex:
        print(f"public {eid} check_access FAIL", str(ex)[:100])

for eid in [2, 52]:
    try:
        Pub.browse(eid).web_read({"display_name": {}, "parent_id": {"fields": {"display_name": {}}}})
        print(f"public {eid} web_read OK")
    except Exception as ex:
        print(f"public {eid} web_read FAIL", str(ex)[:120])

# user 8 open
try:
    env["res.users"].with_user(u85).browse(8).web_read({"name": {}, "login": {}})
    Emp.browse(2).web_read({"display_name": {}, "parent_id": {"fields": {"display_name": {}}}})
    print("user8 + emp2 flow OK")
except Exception as ex:
    print("flow FAIL", str(ex)[:200])

# vanilla super path without lug?
r2 = Pub.browse(2)
result = super(type(r2), r2)._check_access("read")
print("super _check_access 2", result)
