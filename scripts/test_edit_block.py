# -*- coding: utf-8 -*-
import traceback

user = env["res.users"].sudo().browse(58)
vp = env["hr.employee"].sudo().search([("mien", "=", "VP")], limit=1)
store = env["hr.employee"].sudo().search([("mien", "=", "Nam")], limit=1)
Employee = env["hr.employee"].with_user(user)

for label, emp in [("VP", vp), ("Nam", store)]:
    if not emp:
        print(label, "no employee")
        continue
    try:
        with env.cr.savepoint():
            emp_u = Employee.browse(emp.id)
            old = emp_u.ghi_chu or ""
            emp_u.write({"ghi_chu": old + ""})
            print(label, "WRITE OK")
    except Exception:
        print(label, "BLOCKED")
        traceback.print_exc(limit=2)

try:
    with env.cr.savepoint():
        v = env["hr.version"].with_user(user).browse(vp.version_id.id)
        v.write({"job_title": v.job_title or "test"})
        print("version WRITE OK")
except Exception:
    print("version BLOCKED")
    traceback.print_exc(limit=2)
