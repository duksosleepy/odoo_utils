# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

u = env["res.users"].browse(85)
Leave = env["hr.leave"].with_user(u)
leaves = Leave.search([])
print("readable leaves", len(leaves))
for lv in leaves:
    emp = lv.employee_id
    emp_id = emp.id
    emp_mien = env["hr.employee"].sudo().browse(emp_id).mien if emp_id else None
    emp_readable = False
    try:
        env["hr.employee.public"].with_user(u).browse(emp_id).check_access("read")
        emp_readable = True
    except Exception:
        pass
    print(f"  leave {lv.id} emp={emp_id} mien={emp_mien} emp_readable={emp_readable} state={lv.state}")

# ir.rules on hr.leave
print("\n=== hr.leave rules for user ===")
Rule = env["ir.rule"]
rules = Rule.with_user(u)._get_rules("hr.leave", "read")
for r in rules:
    print(" ", r.id, r.name, r.domain_force[:120] if r.domain_force else "")

# Try loading time off dashboard action
print("\n=== simulate employee_id fetch on leave ===")
lv = env["hr.leave"].with_user(u).browse(41)
try:
    print("leave 41 employee", lv.employee_id.name)
except Exception as ex:
    print("FAIL", type(ex).__name__, ex)
