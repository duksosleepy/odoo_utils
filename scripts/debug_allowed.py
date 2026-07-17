# -*- coding: utf-8 -*-
u = env["res.users"].sudo().browse(58)
z = u.lug_hr_employee_edit_mien_zone_ids
for x in z:
    print("zone", x.id, (x.legacy_mien or "").encode("unicode_escape").decode())
a = u.lug_allowed_employee_edit_legacy_miens()
print("allowed is None", a is None)
if a is not None:
    print("allowed", [m.encode("unicode_escape").decode() for m in a])
