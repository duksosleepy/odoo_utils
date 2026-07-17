# -*- coding: utf-8 -*-
u = env["res.users"].sudo().browse(85)
UserPub = env["hr.employee.public"].with_user(u)
r81 = UserPub.browse(81)
try:
    data = r81.web_read({"parent_id": {"fields": {"display_name": {}}}})
    print("OK", data)
except Exception as e:
    print("FAIL", type(e).__name__, str(e)[:120].encode("unicode_escape").decode())
