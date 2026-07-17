# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
Pub = env["hr.employee.public"].with_user(u85)

# parent 52 visibility
e52 = env["hr.employee"].sudo().browse(52)
print("e52 mien", e52.mien, "name", e52.name)
try:
    Pub.browse(52).check_access("read")
    print("e52 public check_access OK")
except Exception as ex:
    print("e52 public check_access FAIL", str(ex)[:150])

try:
    Pub.browse(2).web_read({"name": {}, "parent_id": {"fields": {"display_name": {}}}})
    print("e2 with parent OK", Pub.browse(2).web_read({"parent_id": {"fields": {"display_name": {}}}})[0].get("parent_id"))
except Exception as ex:
    print("e2 parent FAIL", str(ex)[:200])

# action_open_employees from user 8 as anh.trinh
act = env["res.users"].with_user(u85).browse(8).action_open_employees()
print("action", act)
model = act["res_model"]
rid = act["res_id"]
rec = env[model].with_user(u85).browse(rid)
try:
    rec.web_read({"display_name": {}, "name": {}, "parent_id": {"fields": {"display_name": {}}}})
    print("action target web_read OK")
except Exception as ex:
    print("action target FAIL", str(ex)[:200])

# LUG group open users
grp = env["lug.group"].sudo().search([], limit=1)
if grp:
    for uid in grp.user_ids.ids:
        if "miennam" in (env["res.users"].sudo().browse(uid).login or ""):
            print("in lug group", uid)
