# -*- coding: utf-8 -*-
emps = env["hr.employee"].sudo().search([("employee_visibility", "=", "office")], limit=20)
for e in emps:
    print(
        e.id,
        "mien", repr(e.mien),
        "zone", e.mien_zone_id.id if e.mien_zone_id else None,
        "legacy", repr(e._lug_employee_legacy_mien()),
    )

vp_zone = env["hr.mien.zone"].sudo().search([("legacy_mien", "=", "VP")], limit=1)
vp_by_zone = env["hr.employee"].sudo().search([("mien_zone_id", "=", vp_zone.id)], limit=5)
print("vp zone count", env["hr.employee"].sudo().search_count([("mien_zone_id", "=", vp_zone.id)]))
for e in vp_by_zone:
    print("by zone", e.id, repr(e.mien), repr(e._lug_employee_legacy_mien()))
