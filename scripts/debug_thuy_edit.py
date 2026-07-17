# -*- coding: utf-8 -*-
Users = env["res.users"].sudo()
u = Users.search([("login", "ilike", "thuy")], limit=5)
if not u:
    u = Users.search([("name", "ilike", "Thu")], limit=5)
for x in u:
    allowed = x.lug_allowed_employee_edit_legacy_miens()
    print(
        "user", x.id, x.login.encode("unicode_escape").decode(),
        "policy", x.lug_hr_employee_edit_policy,
        "zones", [z.legacy_mien.encode("unicode_escape").decode() for z in x.lug_hr_employee_edit_mien_zone_ids],
        "allowed", "ALL" if allowed is None else sorted(allowed),
        "hr_mgr", x.has_group("hr.group_hr_manager"),
        "system", x.has_group("base.group_system"),
    )

vp = env["hr.employee"].sudo().search([("mien", "=", "VP")], limit=1)
if vp:
    print("vp emp", vp.id, "mien", vp.mien, "legacy", vp._lug_employee_legacy_mien())
