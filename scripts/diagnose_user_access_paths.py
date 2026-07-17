# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
for uid in [8, 58, 85]:
    try:
        env["res.users"].with_user(u85).browse(uid).check_access("read")
        print(f"user {uid} read OK")
    except Exception as ex:
        print(f"user {uid} read FAIL", str(ex)[:100])

# avatar card / discuss path
Pub = env["hr.employee.public"].with_user(u85)
try:
    Pub.browse(2).get_avatar_card_data(["display_name", "job_title"])
    print("avatar card OK")
except Exception as ex:
    print("avatar card FAIL", str(ex)[:150])

try:
    act = Pub.browse(2).get_formview_action()
    Pub.browse(2).web_read({"display_name": {}, "name": {}, "job_title": {}})
    print("public formview OK", act.get("res_model"))
except Exception as ex:
    print("public formview FAIL", str(ex)[:150])

# Simulate hrm_detail broken path - super only
r = Pub.browse(33)
print("emp33 lug _check_access", r._check_access("read"))
try:
    r.check_access("read")
    print("emp33 should deny but check_access says OK - BUG")
except Exception as ex:
    print("emp33 correctly denied")
