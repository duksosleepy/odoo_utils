# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
Pub = env["hr.employee.public"].with_user(u85)
mixin = env["hr.employee.access.mixin"]

print("user-linked refs", mixin._hr_employee_access_user_linked_reference_readable_ids(u85))
print("all refs sample", mixin._hr_employee_access_reference_readable_ids(u85)[:15])

for eid in [2, 52, 33]:
    try:
        Pub.browse(eid).check_access("read")
        print(f"emp {eid} OK")
    except Exception as ex:
        print(f"emp {eid} FAIL", str(ex)[:80])

# admin.miennam user open
Pub.browse(81)._hr_employee_read_is_restricted()
try:
    env["res.users"].with_user(u85).browse(8).web_read({"name": {}, "login": {}})
    Pub.browse(2).web_read({"display_name": {}, "parent_id": {"fields": {"display_name": {}}}})
    print("admin.miennam flow OK")
except Exception as ex:
    print("admin.miennam flow FAIL", str(ex)[:200])
