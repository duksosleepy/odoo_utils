# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
print("groups:", [g.name for g in u85.group_ids if 'hr' in (g.name or '').lower() or 'lug' in (g.name or '').lower()][:15])
print("hr_user", u85.has_group("hr.group_hr_user"))
print("hr_manager", u85.has_group("hr.group_hr_manager"))

Emp = env["hr.employee"].with_user(u85)
for eid in [8, 71]:
    try:
        Emp.browse(eid).check_access("read")
        print(f"hr.employee {eid} check_access OK")
    except Exception as ex:
        print(f"hr.employee {eid} check_access FAIL", str(ex)[:200])

# action used when opening employee from menu
act = env.ref("hr.open_view_employee_list_my", raise_if_not_found=False)
if act:
    print("action res_model", act.res_model)

# Try opening employee form action for hr users
for xmlid in ["hr.open_view_employee_list_my", "hr.hr_employee_public_action", "hr.hr_employee_public_action"]:
    try:
        a = env.ref(xmlid)
        print(xmlid, "->", a.res_model)
    except Exception:
        pass

# Simulate kanban click load
Pub = env["hr.employee.public"].with_user(u85)
domain = env["hr.employee.access.mixin"]._hr_employee_visibility_read_domain(u85, model_name="hr.employee.public")
print("visibility domain", domain)
print("emp8 in domain search", bool(Pub.search([("id","=",8)] + (domain if isinstance(domain, list) else []), limit=1)))

# Check if emp 8 active in public table
env.cr.execute("SELECT id FROM hr_employee_public WHERE id=8")
print("public row", env.cr.fetchone())
