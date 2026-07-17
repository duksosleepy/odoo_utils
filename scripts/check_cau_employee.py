# -*- coding: utf-8 -*-
user = env["res.users"].sudo().search([("login", "=", "admin.lug@sangtam.com")], limit=1)
emp = env["hr.employee"].sudo().search([("name", "ilike", "Doan")], limit=5)
if not emp:
    emp = env["hr.employee"].sudo().search([("name", "ilike", "Cau")], limit=5)
for e in emp:
    print(
        "emp", e.id,
        "name", e.name.encode("unicode_escape").decode(),
        "mien", repr(e.mien),
        "zone", e.mien_zone_id.id if e.mien_zone_id else None,
        "legacy", repr(e._lug_employee_legacy_mien()),
        "visibility", e.employee_visibility,
    )
