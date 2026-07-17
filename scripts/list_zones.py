# -*- coding: utf-8 -*-
zones = env["hr.mien.zone"].sudo().search([])
for z in zones:
    print(z.id, (z.legacy_mien or "").encode("unicode_escape").decode())

u = env["res.users"].sudo().search([("login", "=", "admin.lug@sangtam.com")], limit=1)
if u:
    print("admin policy", u.lug_hr_employee_edit_policy)
    print("admin zone ids", u.lug_hr_employee_edit_mien_zone_ids.ids)
