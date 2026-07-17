# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
e7 = env["hr.employee"].sudo().browse(7)
print("emp 7 exists:", e7.exists(), "name:", e7.name if e7.exists() else None, "active:", e7.active if e7.exists() else None)
user = env["res.users"].browse(61)
emp56 = user.employee_id
print("user 61:", user.login, "emp:", emp56.id, emp56.name, "mien:", emp56.mien)
# can user 61 read emp 7?
try:
    env["hr.employee"].with_user(user).browse(7).check_access("read")
    print("hr.employee 7 read: OK")
except Exception as ex:
    print("hr.employee 7 read: FAIL", ex)
try:
    env["hr.employee.public"].with_user(user).browse(7).check_access("read")
    print("hr.employee.public 7 read: OK")
except Exception as ex:
    print("hr.employee.public 7 read: FAIL", ex)
# visible handover candidates for khan
Leave = env["hr.leave"].with_user(user)
leave = Leave.new({"employee_id": emp56.id})
ctx = leave._with_handover_employee_read_context().env.context
print("handover read context keys:", [k for k in ctx if "handover" in k or "employee" in k or "lug" in k])
