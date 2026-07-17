# -*- coding: utf-8 -*-
user = env["res.users"].browse(85)
UserPub = env["hr.employee.public"].with_user(user)
r44 = UserPub.browse(44)
try:
    print("web_read 44", r44.web_read({"display_name": {}}))
except Exception as e:
    print("web_read 44 FAIL", type(e).__name__)
