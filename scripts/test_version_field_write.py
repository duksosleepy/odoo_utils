# -*- coding: utf-8 -*-
user = env["res.users"].sudo().browse(58)
vp = env["hr.employee"].sudo().search([("mien", "=", "VP")], limit=1)
Employee = env["hr.employee"].with_user(user)

try:
    with env.cr.savepoint():
        emp_u = Employee.browse(vp.id)
        emp_u.write({"job_title": emp_u.job_title or "test"})
        print("employee.write job_title OK")
except Exception as e:
    print("employee.write job_title BLOCKED", type(e).__name__)

try:
    with env.cr.savepoint():
        emp_u = Employee.browse(vp.id)
        emp_u.write({"mien": "VP"})
        print("employee.write mien OK")
except Exception as e:
    print("employee.write mien BLOCKED", type(e).__name__)
