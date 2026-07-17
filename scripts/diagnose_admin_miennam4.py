# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

e2 = env["hr.employee"].sudo().browse(2)
print("e2 parent", e2.parent_id.id, e2.parent_id.name if e2.parent_id else None, "mien", e2.parent_id.mien if e2.parent_id else None)
print("e2 coach", e2.coach_id.id if e2.coach_id else None)
print("children", e2.child_ids.ids)

u85 = env["res.users"].browse(85)
Pub = env["hr.employee.public"].with_user(u85)
Emp = env["hr.employee"].with_user(u85)

# get_formview_action paths
for model in ["hr.employee", "hr.employee.public", "res.users"]:
    rec = env[model].browse(2 if model != "res.users" else 8)
    try:
        act = rec.with_user(u85).get_formview_action()
        print(model, "form action", act.get("res_model"), act.get("res_id"))
    except Exception as ex:
        print(model, "form action FAIL", str(ex)[:120])

# child_ids web_read on e2
try:
    Emp.browse(2).web_read({"child_ids": {"fields": {"display_name": {}}}})
    print("child_ids web_read OK")
except Exception as ex:
    print("child_ids FAIL", str(ex)[:200])

# Simulate opening user 8 from lug - full user form fields
User = env["res.users"].with_user(u85)
view = User.get_view(view_type="form")
import re
fields = set(re.findall(r'name="([^"]+)"', view["arch"]))
print("user form fields count", len(fields))

# Try read employee via res.users action_open_employee
u8 = User.browse(8)
if hasattr(u8, "action_open_employee"):
    try:
        act = u8.action_open_employee()
        print("action_open_employee", act)
    except Exception as ex:
        print("action_open_employee FAIL", ex)

# hr.employee get_formview_action for emp 2 as user 85
try:
    act = Emp.browse(2).get_formview_action()
    print("emp get_formview", act)
    # load that form
    if act.get("res_model") == "hr.employee.public":
        Pub.browse(2).web_read({"display_name": {}, "name": {}})
        print("public form load OK")
except Exception as ex:
    print("emp formview FAIL", str(ex)[:200])
