# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u = env["res.users"].browse(85)
Emp = env["hr.employee"].with_user(u)

print("hr.employee search", Emp.search_count([]))
print("hr.employee ids", Emp.search([]).ids[:10])

try:
    Emp.search([]).check_access("read")
    print("hr.employee batch OK")
except Exception as e:
    print("hr.employee batch FAIL", str(e)[:200])

try:
    Emp.browse(44).check_access("read")
    print("hr.employee 44 OK")
except Exception as e:
    print("hr.employee 44 FAIL", str(e)[:200])

# Which action/menu?
print("has hr_user", u.has_group("hr.group_hr_user"))
