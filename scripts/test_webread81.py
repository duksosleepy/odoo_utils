# -*- coding: utf-8 -*-
user = env["res.users"].browse(85)
r81 = env["hr.employee.public"].with_user(user).browse(81)
try:
    data = r81.web_read({"parent_id": {"fields": {"display_name": {}}}})
    parent = data[0].get("parent_id")
    print("OK", parent)
except Exception as e:
    print("FAIL", type(e).__name__, repr(str(e)[:200]))
