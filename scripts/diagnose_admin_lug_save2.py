# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u = env["res.users"].browse(58)
Emp = env["hr.employee"].with_user(u)
UserPub = env["hr.employee.public"].with_user(u)

def full_save_test(eid):
    print(f"\n--- save test emp {eid} ---")
    e = Emp.browse(eid)
    UserPub.browse(eid)._hr_employee_read_is_restricted()
    phone = (e.work_phone or "0900000000")
    new_phone = phone if phone != "0900000001" else "0900000002"
    try:
        e.write({"work_phone": new_phone})
        print("write OK")
    except Exception as ex:
        print("write FAIL", str(ex)[:180])
        return
    try:
        UserPub.browse(eid).web_read({"display_name": {}, "work_phone": {}, "parent_id": {"fields": {"display_name": {}}}})
        print("public web_read after write OK")
    except Exception as ex:
        print("public web_read after write FAIL", str(ex)[:180])
    try:
        e.web_read({"display_name": {}, "work_phone": {}, "parent_id": {"fields": {"display_name": {}}}})
        print("employee web_read after write OK")
    except Exception as ex:
        print("employee web_read after write FAIL", str(ex)[:180])

for eid in [33, 21, 51, 52]:
    full_save_test(eid)

# VP visible but not editable
full_save_test(2)
