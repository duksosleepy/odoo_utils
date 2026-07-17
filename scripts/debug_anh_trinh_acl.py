# -*- coding: utf-8 -*-
u = env["res.users"].sudo().search([("login", "=", "anh.trinh@sangtam.com")], limit=1)
print("lug_perm_user", u.has_group("lug_permission.group_lug_permission_user"))
print("lug_perm_manager", u.has_group("lug_permission.group_lug_permission_manager"))

UserEnv = env["res.users"].with_user(u)
try:
    me = UserEnv.browse(u.id)
    data = me.read(["name", "lug_hr_employee_edit_policy", "lug_hr_employee_edit_mien_zone_ids", "lug_group_ids"])
    print("read self OK", data[0].keys())
except Exception as e:
    print("read self FAIL", type(e).__name__, str(e)[:120].encode("unicode_escape").decode())

try:
    me.read(["lug_user_permission_ids"])
    print("lug_user_permission_ids OK")
except Exception as e:
    print("lug_user_permission_ids FAIL", type(e).__name__)

try:
    env["lug.group"].with_user(u).search([])
    print("lug.group search OK")
except Exception as e:
    print("lug.group search FAIL", type(e).__name__)

try:
    env["hr.mien.zone"].with_user(u).search([])
    print("hr.mien.zone search OK")
except Exception as e:
    print("hr.mien.zone search FAIL", type(e).__name__)
