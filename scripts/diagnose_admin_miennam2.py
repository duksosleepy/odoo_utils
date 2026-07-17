# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
u8 = env["res.users"].sudo().browse(8)
Pub = env["hr.employee.public"].with_user(u85)

print("target user 8 employee", u8.employee_id.id)

# Simulate user form open
try:
    u8.with_user(u85).web_read({
        "name": {},
        "login": {},
        "employee_id": {"fields": {"display_name": {}}},
        "employee_ids": {"fields": {"display_name": {}}},
    })
    print("user web_read OK")
except Exception as ex:
    print("user web_read FAIL", type(ex).__name__, str(ex)[:200])

# Employee 2 after cache poison
Pub.browse(81)._hr_employee_read_is_restricted()
try:
    Pub.browse(2).check_access("read")
    print("emp2 after poison check_access OK")
except Exception as ex:
    print("emp2 after poison FAIL", str(ex)[:150])

try:
    Pub.browse(2).web_read({"display_name": {}, "parent_id": {"fields": {"display_name": {}}}})
    print("emp2 web_read OK")
except Exception as ex:
    print("emp2 web_read FAIL", str(ex)[:200])

# Employee 44 (org ref)
e44 = env["hr.employee"].sudo().browse(44)
print("e44", e44.name, "mien", e44.mien)
try:
    Pub.browse(44).check_access("read")
    print("e44 check_access OK")
except Exception as ex:
    print("e44 check_access FAIL", str(ex)[:150])

# Open employee 2 form full
Emp = env["hr.employee"].with_user(u85)
try:
    Emp.browse(2).web_read({"display_name": {}, "name": {}, "parent_id": {"fields": {"display_name": {}}}})
    print("emp2 form web_read OK")
except Exception as ex:
    print("emp2 form FAIL", str(ex)[:200])
