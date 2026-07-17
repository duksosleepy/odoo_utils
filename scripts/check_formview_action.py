# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
for eid in [8, 71]:
    for model_name in ["hr.employee", "hr.employee.public"]:
        M = env[model_name].with_user(u85)
        rec = M.browse(eid)
        try:
            act = rec.get_formview_action()
            print(f"{model_name} {eid} action model={act.get('res_model')} id={act.get('res_id')}")
            rec.check_access("read")
            print("  check_access OK")
        except Exception as ex:
            print(f"{model_name} {eid} FAIL", str(ex)[:200])

# avatar card
for eid in [8, 71]:
    try:
        d = env["hr.employee.public"].with_user(u85).browse(eid).get_avatar_card_data(["display_name", "job_title"])
        print(f"avatar {eid} OK", d)
    except Exception as ex:
        print(f"avatar {eid} FAIL", str(ex)[:200])
