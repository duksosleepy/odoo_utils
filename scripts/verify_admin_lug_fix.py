# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

env["res.users"]._lug_set_default_employee_edit_scopes()
u = env["res.users"].sudo().browse(58)
print("=== admin.lug after fix ===")
print("visibility", u.visibility_policy, "scope", u.lug_data_scope)
print("edit_zones", u.lug_hr_employee_edit_mien_zone_ids.mapped("legacy_mien"))

mixin = env["hr.employee.access.mixin"]
print("policy domain", mixin._hr_employee_policy_domain(u))

UserPub = env["hr.employee.public"].with_user(u)
Emp = env["hr.employee"].with_user(u)
for m in ["Nam", "ĐTT", "Bắc", "VP"]:
    print(m, "visible", UserPub.search_count([("mien", "=", m)]), "/", env["hr.employee"].sudo().search_count([("mien", "=", m)]))

print("total visible", UserPub.search_count([]))

# Save test on previously hidden employee 4
e4 = Emp.browse(4)
print("emp4 visible", bool(UserPub.search([("id", "=", 4)], limit=1)), "edit", e4._lug_is_employee_profile_edit_allowed())
UserPub.browse(4)._hr_employee_read_is_restricted()
try:
    e4.write({"work_phone": e4.work_phone or "0900111222"})
    print("write emp4 OK")
    UserPub.browse(4).web_read({"display_name": {}, "parent_id": {"fields": {"display_name": {}}}})
    print("read emp4 after write OK")
except Exception as ex:
    print("emp4 FAIL", str(ex)[:180])

# Kanban
try:
    data = UserPub.web_search_read([], {"display_name": {}}, limit=80)
    print("kanban OK", len(data.get("records", data)))
except Exception as ex:
    print("kanban FAIL", str(ex)[:180])
