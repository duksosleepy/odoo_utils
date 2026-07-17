# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
for uid in [13, 76]:
    u = env["res.users"].with_user(u85).browse(uid)
    act = u.get_formview_action()
    print("user", uid, "form action", act.get("res_model"), act.get("res_id"))
    if u.employee_id:
        eact = u.employee_id.with_user(u85).get_formview_action()
        print("  employee action", eact.get("res_model"), eact.get("res_id"))
        try:
            env[eact["res_model"]].with_user(u85).browse(eact["res_id"]).check_access("read")
            print("  employee open OK")
        except Exception as ex:
            print("  employee open FAIL", ex)
