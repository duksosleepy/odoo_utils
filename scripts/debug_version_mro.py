# -*- coding: utf-8 -*-
import inspect
Version = env["hr.version"]
for cls in Version.__class__.mro()[:15]:
    if "write" in cls.__dict__:
        print("write in", cls.__module__, cls.__name__)

v = env["hr.version"].browse(2)
# call our method directly
try:
    v._lug_check_version_profile_edit_access()
    print("direct check passed")
except Exception as e:
    print("direct check failed", type(e).__name__)

user = env["res.users"].sudo().browse(58)
v_user = env["hr.version"].with_user(user).browse(2)
try:
    v_user._lug_check_version_profile_edit_access()
    print("user check passed")
except Exception as e:
    print("user check failed", type(e).__name__)
