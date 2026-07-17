# -*- coding: utf-8 -*-
for login in ["admin.lug@sangtam.com", "anh.trinh@sangtam.com"]:
    u = env["res.users"].sudo().search([("login", "=", login)], limit=1)
    if not u:
        print(login, "NOT FOUND")
        continue
    allowed = u.lug_allowed_employee_edit_legacy_miens()
    zone_ids = u.lug_hr_employee_edit_mien_zone_ids.ids
    print(login, "policy=", u.lug_hr_employee_edit_policy, "zone_ids=", zone_ids, "allowed=", "ALL" if allowed is None else len(allowed))
