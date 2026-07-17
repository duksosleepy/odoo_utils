# -*- coding: utf-8 -*-
user = env["res.users"].sudo().search([("login", "=", "admin.lug@sangtam.com")], limit=1)
emp = env["hr.employee"].sudo().browse(10)
legacy = emp._lug_employee_legacy_mien()
allowed = user.lug_allowed_employee_edit_legacy_miens()
print("legacy", repr(legacy))
print("allowed_none", allowed is None)
if allowed is not None:
    print("in_allowed", legacy in allowed)

Employee = env["hr.employee"].with_user(user)
try:
    with env.cr.savepoint():
        Employee.browse(10).write({"ghi_chu": "test"})
        print("WRITE OK")
except Exception:
    print("BLOCKED")
