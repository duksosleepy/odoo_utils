# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
u = env["res.users"].browse(85)
own = u.sudo().employee_id
print("own", own, own._name, own.id)
print("own.parent_id raw", own.parent_id, own.read(["parent_id"]))
emp = env["hr.employee"].sudo().browse(81)
print("sudo browse parent", emp.parent_id.id, emp.read(["parent_id"]))
print("fields", emp._fields["parent_id"])
pub = env["hr.employee.public"].sudo().browse(81)
print("public parent", pub.parent_id.id, pub.read(["parent_id"]))
m = env["hr.employee.access.mixin"]
print("org refs", m._hr_employee_access_org_reference_readable_ids(u))
