# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

u = env["res.users"].browse(85)
Cal = env["hr.leave.report.calendar"].with_user(u)
rows = Cal.search([])
print("calendar rows", len(rows))
for r in rows:
    emp_id = r.sudo().employee_id.id if hasattr(r, "employee_id") else None
    emp_mien = env["hr.employee"].sudo().browse(emp_id).mien if emp_id else None
    readable = False
    if emp_id:
        try:
            env["hr.employee.public"].with_user(u).browse(emp_id).check_access("read")
            readable = True
        except Exception:
            pass
    print(f"  cal {r.id} emp {emp_id} mien {emp_mien} emp_readable {readable}")
    try:
        r.web_read({"employee_id": {"fields": {"display_name": {}}}, "name": {}})
        print("    web_read OK")
    except Exception as ex:
        print("    web_read FAIL", type(ex).__name__, str(ex)[:120])
