# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
u = env["res.users"].sudo().browse(85)
print("user_role", u.user_role)
print("visibility", u.visibility_policy)
print("department", u.employee_department_id.id if u.employee_department_id else None)
