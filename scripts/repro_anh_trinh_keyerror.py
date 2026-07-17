# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u = env["res.users"].browse(85)
Emp = env["hr.employee"].with_user(u)

# Find VP employees referencing 88
for e in env["hr.employee"].sudo().search([("mien", "=", "VP")]):
    for fname in ["parent_id", "coach_id"]:
        rel = getattr(e, fname)
        if rel.id == 88:
            print(f"emp {e.id} {e.name} {fname}=88")

# Who has parent 88?
env.cr.execute("SELECT id, name FROM hr_employee WHERE parent_id=88 OR coach_id=88")
for row in env.cr.fetchall():
    print("refs 88:", row)

# Reproduce web_read on emp 37 (VP sample)
e37 = Emp.browse(37)
env.cr.execute("SELECT parent_id, coach_id FROM hr_employee WHERE id=37")
print("e37 fk", env.cr.fetchone())

# Minimal repro - try opening e88 form
for eid in [88, 37, 2]:
    try:
        e = Emp.browse(eid)
        spec = {
            "display_name": {},
            "name": {},
            "parent_id": {"fields": {"display_name": {}}},
            "coach_id": {"fields": {"display_name": {}}},
            "department_id": {"fields": {"display_name": {}}},
            "job_id": {"fields": {"display_name": {}}},
            "work_phone": {},
            "mien": {},
            "mien_zone_id": {"fields": {"display_name": {}}},
            "employee_form_force_readonly_ui": {},
        }
        data = e.web_read(spec)
        print(f"web_read {eid} OK")
    except Exception as ex:
        print(f"web_read {eid} FAIL", type(ex).__name__, str(ex)[:200])
