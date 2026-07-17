# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

# find Cao Thi Trang
for term in ["Cao", "Trang", "cao", "trang"]:
    emps = env["hr.employee"].sudo().search([("name", "ilike", term)])
    for e in emps:
        if "cao" in (e.name or "").lower() or "trang" in (e.name or "").lower():
            print("emp", e.id, repr(e.name), "mien", e.mien, "active", e.active)

env.cr.execute("SELECT id, name, mien, active, user_id FROM hr_employee WHERE name ILIKE %s", ("%Cao%Trang%",))
for row in env.cr.fetchall():
    print("sql", row)

env.cr.execute("SELECT id, name, mien, active FROM hr_employee WHERE name ILIKE %s", ("%Trang%",))
for row in env.cr.fetchall():
    print("trang", row)

# emp 71 thanh.thach details
e71 = env["hr.employee"].sudo().browse(71)
print("\nthanh emp71", e71.name, "mien", e71.mien, "user", e71.user_id.login)

u85 = env["res.users"].browse(85)
Pub = env["hr.employee.public"].with_user(u85)
print("71 visible", bool(Pub.search([("id", "=", 71)], limit=1)))
print("71 in refs", 71 in env["hr.employee.access.mixin"]._hr_employee_access_reference_readable_ids(u85))
