# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].sudo().browse(85)
print("anh.trinh scope", u85.lug_data_scope, "visibility", u85.visibility_policy, "mien", u85.employee_mien)
print("edit zones", u85.lug_hr_employee_edit_mien_zone_ids.mapped("legacy_mien"))

Pub = env["hr.employee.public"].with_user(u85)
Emp = env["hr.employee"].with_user(u85)
mixin = env["hr.employee.access.mixin"]

def show_person(label, search_name):
    print(f"\n=== {label} ({search_name}) ===")
    emps = env["hr.employee"].sudo().search([("name", "ilike", search_name)])
    users = env["res.users"].sudo().search(["|", ("name", "ilike", search_name), ("login", "ilike", search_name)])
    for e in emps:
        print("emp", e.id, e.name, "mien", e.mien, "user", e.user_id.login if e.user_id else None,
              "parent", e.parent_id.id, e.parent_id.name if e.parent_id else None,
              "dept", e.department_id.name if e.department_id else None)
        vis = bool(Pub.search([("id", "=", e.id)], limit=1))
        print("  in VP search", Pub.search_count([("id", "=", e.id), ("mien", "=", "VP")]))
        print("  in public search", vis)
        try:
            Pub.browse(e.id).check_access("read")
            print("  check_access OK")
        except Exception as ex:
            print("  check_access FAIL", str(ex)[:120])
        try:
            Emp.browse(e.id).web_read({"display_name": {}, "name": {}})
            print("  web_read OK")
        except Exception as ex:
            print("  web_read FAIL", str(ex)[:120])
    for u in users:
        print("user", u.id, u.login, u.name, "emp", u.employee_id.id if u.employee_id else None)
        try:
            u.with_user(u85).check_access("read")
            print("  user read OK")
        except Exception as ex:
            print("  user read FAIL", str(ex)[:100])

show_person("Cao Thi Trang", "Cao Thị Trang")
show_person("Thanh Thach", "thanh.thach")

print("\nrefs", mixin._hr_employee_access_reference_readable_ids(u85)[:20])
print("VP visible count", Pub.search_count([("mien", "=", "VP")]))
