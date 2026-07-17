# -*- coding: utf-8 -*-
u = env["res.users"].browse(85)
print("user", u.login, "employee_id", u.sudo().employee_id.id)
for emp in env["hr.employee"].sudo().search([("user_id", "=", 85)]):
    print("emp by user", emp.id, emp.name, "parent", emp.parent_id.id, emp.parent_id.name)
own = u.sudo().employee_id
if own:
    print("own exists", own.id, own.name)
    v = own.sudo().current_version_id
    print("version", v.id if v else None, "parent", v.parent_id.id if v and v.parent_id else None)
else:
    print("no employee linked")
# check id 44
e44 = env["hr.employee"].sudo().browse(44)
print("e44 exists", e44.exists(), e44.name if e44.exists() else "N/A")
