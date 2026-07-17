# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u = env["res.users"].sudo().browse(85)
print("login", u.login)
print("lug_scope", u.lug_data_scope, "visibility", u.visibility_policy)
print("edit_policy", u.lug_hr_employee_edit_policy)
print("edit_zones", u.lug_hr_employee_edit_mien_zone_ids.mapped("legacy_mien"))
print("employee_mien", u.employee_mien)
print("hr_user", u.has_group("hr.group_hr_user"))
print("edit_allowed grp", u.has_group("hr_employee_self_only.group_hr_employee_edit_allowed"))

Emp = env["hr.employee"].with_user(u)
Pub = env["hr.employee.public"].with_user(u)
print("VP visible emp", Emp.search_count([("mien", "=", "VP")]))
print("VP ids sample", Emp.search([("mien", "=", "VP")], limit=5).ids)

e88 = env["hr.employee"].sudo().browse(88)
if e88.exists():
    print("e88", e88.name, "mien", e88.mien, "parent", e88.parent_id.id, e88.department_id.id)

# Who references 88?
for e in env["hr.employee"].sudo().search([("mien", "=", "VP")], limit=15):
    refs = []
    if e.parent_id.id == 88: refs.append("parent")
    if e.coach_id.id == 88: refs.append("coach")
    if refs:
        print("VP emp", e.id, e.name, "refs 88 as", refs)
