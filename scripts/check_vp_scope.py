# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
u85 = env["res.users"].browse(85)
Pub = env["hr.employee.public"].with_user(u85)
for m in ["VP", "Nam", "Bắc"]:
    total = env["hr.employee"].sudo().search_count([("mien", "=", m)])
    vis = Pub.search_count([("mien", "=", m)])
    print(m, "visible", vis, "/", total)
# test Nam employee 33
try:
    Pub.browse(33).check_access("read")
    print("emp33 check OK")
except Exception as ex:
    print("emp33 check FAIL", str(ex)[:100])
