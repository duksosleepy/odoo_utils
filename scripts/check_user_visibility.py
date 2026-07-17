# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
Users = env["res.users"].with_user(u85)
for uid in [13, 76]:
    u = env["res.users"].sudo().browse(uid)
    vis = bool(Users.search([("id", "=", uid)], limit=1))
    print(uid, u.login, u.name, "visible", vis)
    try:
        Users.browse(uid).check_access("read")
        print("  check_access OK")
    except Exception as ex:
        print("  check_access FAIL", str(ex)[:200])

# all VP users visible?
vp_emps = env["hr.employee"].sudo().search([("mien", "=", "VP")])
print("VP employees", len(vp_emps))
missing = []
for e in vp_emps:
    if not env["hr.employee.public"].with_user(u85).search([("id", "=", e.id)], limit=1):
        missing.append((e.id, e.name))
print("VP not visible in public", missing)
