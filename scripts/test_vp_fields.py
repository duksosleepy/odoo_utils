# -*- coding: utf-8 -*-
emp = env["hr.employee"].sudo().browse(2)
print("id", emp.id, "mien", repr(emp.mien), "legacy", repr(emp._lug_employee_legacy_mien()))

user = env["res.users"].sudo().search([("login", "=", "admin.lug@sangtam.com")], limit=1)
Employee = env["hr.employee"].with_user(user)

for field in ["ghi_chu", "private_email", "private_phone", "emergency_contact"]:
    if field not in env["hr.employee"]._fields:
        print(field, "NO FIELD")
        continue
    try:
        with env.cr.savepoint():
            e = Employee.browse(2)
            e.write({field: e[field] or "test"})
            print(field, "WRITE OK")
    except Exception as ex:
        print(field, "BLOCKED", type(ex).__name__)
