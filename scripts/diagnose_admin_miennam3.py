# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
for login in env["res.users"].sudo().search([]):
    if "miennam" in (login.login or "").lower() or "miền nam" in (login.name or "").lower():
        print(login.id, login.login, login.name, "emp", login.employee_id.id)

# Try get_view + simulate opening user 8 form via call_kw path
User = env["res.users"].with_user(u85)
u8 = User.browse(8)
try:
    u8.check_access("read")
    print("user 8 read OK")
except Exception as ex:
    print("user 8 read FAIL", ex)

# employee_ids on user form
try:
    data = u8.read(["name", "employee_id", "employee_ids"])
    print("user read", data)
except Exception as ex:
    print("user read FAIL", ex)

# Public read for all employees linked to users anh might open
for uid in [8, 58]:
    emp = env["res.users"].sudo().browse(uid).employee_id
    if not emp:
        continue
    Pub = env["hr.employee.public"].with_user(u85)
    Pub.browse(81)._hr_employee_read_is_restricted()
    try:
        Pub.browse(emp.id).read(["name"])
        print(f"public read emp {emp.id} after poison OK")
    except Exception as ex:
        print(f"public read emp {emp.id} after poison FAIL", str(ex)[:150])
