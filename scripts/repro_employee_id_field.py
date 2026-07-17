# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u = env["res.users"].browse(85)
Emp = env["hr.employee"].with_user(u)
Pub = env["hr.employee.public"].with_user(u)

for eid in [88, 37]:
    print(f"\n=== emp {eid} ===")
    try:
        r = Emp.browse(eid).web_read({"employee_id": {"fields": {"display_name": {}}}})
        print("hr.employee employee_id OK", r)
    except Exception as ex:
        print("hr.employee employee_id FAIL", ex)
    try:
        r = Pub.browse(eid).web_read({"employee_id": {"fields": {"display_name": {}}}})
        print("public employee_id OK", r)
    except Exception as ex:
        print("public employee_id FAIL", ex)
    try:
        r = Emp.browse(eid).web_read({"display_name": {}})
        print("employee display_name OK")
    except Exception as ex:
        print("employee display_name FAIL", ex)
