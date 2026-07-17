# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u = env["res.users"].browse(58)
Emp = env["hr.employee"].with_user(u)
UserPub = env["hr.employee.public"].with_user(u)

# Simulate hr.employee form save reload
e33 = Emp.browse(33)
UserPub.browse(33)._hr_employee_read_is_restricted()  # poison cache

try:
    e33.web_read({"name": {}, "parent_id": {"fields": {"display_name": {}}}, "department_id": {"fields": {"display_name": {}}}})
    print("hr.employee web_read 33 OK")
except Exception as ex:
    print("hr.employee web_read 33 FAIL", str(ex)[:200])

# version write path
v = e33.current_version_id
try:
    v.write({"work_phone": v.work_phone or ""})
    print("version write OK")
except Exception as ex:
    print("version write FAIL", str(ex)[:200])

try:
    e33.web_read({"name": {}})
    print("post version write web_read OK")
except Exception as ex:
    print("post version write FAIL", str(ex)[:200])

# employee with VP parent outside zone
e21 = Emp.browse(21)
env.cr.execute("SELECT parent_id FROM hr_employee WHERE id=21")
print("e21 parent sql", env.cr.fetchone())
try:
    e21.web_read({"parent_id": {"fields": {"display_name": {}}}})
    print("e21 web_read parent OK", e21.web_read({"parent_id": {"fields": {"display_name": {}}}})[0].get("parent_id"))
except Exception as ex:
    print("e21 web_read FAIL", str(ex)[:200])
