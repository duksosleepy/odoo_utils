# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
for eid in [8, 71]:
    e = env["hr.employee"].sudo().browse(eid)
    v = e.version_id
    print(f"emp {eid} version {v.id if v else None}")
    if v:
        try:
            v.with_user(u85).check_access("read")
            print("  version read OK")
        except Exception as ex:
            print("  version read FAIL", str(ex)[:200])
        try:
            e.with_user(u85).web_read({"version_id": {"fields": {"display_name": {}}}})
            print("  web_read version OK")
        except Exception as ex:
            print("  web_read version FAIL", str(ex)[:200])
