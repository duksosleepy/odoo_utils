# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].sudo().browse(85)
print("groups:", [g.name for g in u85.group_ids if "hr" in (g.name or "").lower() or "lug" in (g.name or "").lower()][:15])
print("lug enforced", u85._lug_permission_is_enforced())
print("hr edit map", u85._lug_effective_permission_map().get("hr"))

Pub = env["hr.employee.public"].with_user(u85)

# Find employees that fail public read for u85
fails = []
for e in env["hr.employee"].sudo().search([]):
    try:
        Pub.browse(e.id).check_access("read")
    except Exception:
        fails.append((e.id, e.name, e.mien))
print("fail count", len(fails), "sample", fails[:10])

# Specifically employees linked to users anh might click
for uid in [8, 58, 57, 1]:
    u = env["res.users"].sudo().browse(uid)
    if not u.exists():
        continue
    emp = u.employee_id
    if not emp:
        print("user", uid, u.login, "no employee")
        continue
    try:
        Pub.browse(emp.id).check_access("read")
        st = "OK"
    except Exception as ex:
        st = str(ex)[:80]
    print(f"user {uid} {u.login} emp {emp.id} mien {emp.mien} -> {st}")

# Open res.users 8 form via web_read common fields
try:
    env["res.users"].with_user(u85).browse(8).web_read({
        "name": {}, "login": {}, "partner_id": {"fields": {"display_name": {}}},
    })
    print("user8 web_read OK")
except Exception as ex:
    print("user8 web_read FAIL", str(ex)[:200])
