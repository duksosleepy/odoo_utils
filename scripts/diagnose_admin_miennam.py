# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].sudo().search([("login", "ilike", "anh.trinh")], limit=1)
targets = env["res.users"].sudo().search([("login", "ilike", "admin.miennam")])
print("anh.trinh", u85.id, u85.login)
for t in targets:
    print("\n=== target", t.id, t.login, t.name, "===")
    emp = t.employee_id
    print("employee", emp.id if emp else None, emp.name if emp else None)
    if emp:
        print("mien", emp.mien, "zone", emp.mien_zone_id.legacy_mien if emp.mien_zone_id else None)
        print("dept", emp.department_id.name if emp.department_id else None)

Pub = env["hr.employee.public"].with_user(u85)
Emp = env["hr.employee"].with_user(u85)

for t in targets:
    if not t.employee_id:
        continue
    eid = t.employee_id.id
    print(f"\n--- access emp {eid} ---")
    try:
        Pub.browse(eid).check_access("read")
        print("public read OK")
    except Exception as ex:
        print("public read FAIL", str(ex)[:120])
    try:
        Emp.browse(eid).check_access("read")
        print("employee read OK")
    except Exception as ex:
        print("employee read FAIL", str(ex)[:120])
    mixin = env["hr.employee.access.mixin"]
    print("org refs", mixin._hr_employee_access_org_reference_readable_ids(u85))
    print("zone parents", mixin._hr_employee_access_zone_parent_reference_readable_ids(u85))
    print("in VP search", bool(Pub.search([("id", "=", eid)], limit=1)))

# anh.trinh own employee parent?
own = u85.employee_id
print("\nown emp", own.id, "parent", own.sudo().parent_id.id, own.sudo().parent_id.name if own.sudo().parent_id else None)
