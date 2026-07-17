# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
env.cr.execute("SELECT id, parent_id, active, company_id, user_id FROM hr_employee WHERE id IN (44, 81)")
print("hr_employee", env.cr.fetchall())
env.cr.execute("SELECT id, parent_id FROM hr_employee_public WHERE id IN (44, 81)")
print("hr_employee_public", env.cr.fetchall())
u = env["res.users"].browse(85)
m = env["hr.employee.access.mixin"]
own = u.sudo().employee_id
print("user employee", own.id)
print("hr.employee parent", env["hr.employee"].sudo().browse(own.id).parent_id.id)
pub = env["hr.employee.public"].sudo().browse(own.id)
print("hr.employee.public parent", pub.parent_id.id)
