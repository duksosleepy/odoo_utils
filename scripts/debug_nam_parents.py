# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
u = env["res.users"].browse(58)
Emp = env["hr.employee"].with_user(u)
UserPub = env["hr.employee.public"].with_user(u)

for e in env["hr.employee"].sudo().search([("mien", "in", ["Nam", "ĐTT", "Bắc"])]):
    pid = e.parent_id.id
    if not pid:
        continue
    parent = env["hr.employee"].sudo().browse(pid)
    vis = bool(UserPub.search([("id", "=", pid)], limit=1))
    if not vis:
        print(f"emp {e.id} {e.name} parent {pid} {parent.name} mien={parent.mien} NOT visible")
        try:
            UserPub.browse(e.id).web_read({"parent_id": {"fields": {"display_name": {}}}})
            print("  web_read OK")
        except Exception as ex:
            print("  web_read FAIL", str(ex)[:120])
