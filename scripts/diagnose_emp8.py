# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
Pub = env["hr.employee.public"].with_user(u85)
Emp = env["hr.employee"].with_user(u85)
mixin = env["hr.employee.access.mixin"]

for eid in [8, 71]:
    e = env["hr.employee"].sudo().browse(eid)
    print(f"\n=== emp {eid} {e.name} mien={e.mien} user={e.user_id.login if e.user_id else None} ===")
    print("policy domain", mixin._hr_employee_policy_domain(u85))
    in_policy = bool(env["hr.employee"].sudo().search_count([("id", "=", eid)] + mixin._hr_employee_policy_domain(u85)))
    print("in policy domain", in_policy)
    refs = mixin._hr_employee_access_reference_readable_ids(u85)
    print("in refs", eid in refs)
    print("public search", bool(Pub.search([("id", "=", eid)], limit=1)))
    try:
        Pub.browse(eid).check_access("read")
        print("check_access OK")
    except Exception as ex:
        print("check_access FAIL", ex)
    try:
        r = Pub.browse(eid).web_read({"name": {}, "display_name": {}})
        print("web_read OK", r)
    except Exception as ex:
        print("web_read FAIL", ex)
    try:
        Emp.browse(eid).web_read({"name": {}})
        print("hr.employee web_read OK")
    except Exception as ex:
        print("hr.employee web_read FAIL", str(ex)[:150])

# user 13 linked to emp 8
u13 = env["res.users"].sudo().browse(13)
print("\nuser 13", u13.login, u13.name)
try:
    u13.with_user(u85).check_access("read")
    print("user13 read OK")
except Exception as ex:
    print("user13 read FAIL", ex)

# How does anh.trinh open profile - via user form?
print("\nuser-linked refs logic:")
print(mixin._hr_employee_access_user_linked_reference_readable_ids(u85))
