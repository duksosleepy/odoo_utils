# -*- coding: utf-8 -*-
env["res.users"]._lug_set_default_employee_edit_scopes()
env.cr.commit()

Users = env["res.users"].sudo()
for login in ["admin.lug@sangtam.com", "anh.trinh@sangtam.com"]:
    u = Users.search([("login", "=", login)], limit=1)
    if not u:
        print(login, "NOT FOUND")
        continue
    allowed = u.lug_allowed_employee_edit_legacy_miens()
    zones = [z.legacy_mien for z in u.lug_hr_employee_edit_mien_zone_ids]
    print(login, "policy=", u.lug_hr_employee_edit_policy, "zones=", zones, "allowed=", "ALL" if allowed is None else sorted(allowed))
