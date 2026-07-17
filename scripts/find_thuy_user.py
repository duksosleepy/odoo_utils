# -*- coding: utf-8 -*-
Users = env["res.users"].sudo()
for term in ["Nguy", "Thu", "thuy"]:
    found = Users.search([("name", "ilike", term)], limit=10)
    for x in found:
        allowed = x.lug_allowed_employee_edit_legacy_miens()
        print(
            x.id,
            x.login.encode("unicode_escape").decode(),
            x.name.encode("unicode_escape").decode(),
            "policy", x.lug_hr_employee_edit_policy,
            "zone_ids", x.lug_hr_employee_edit_mien_zone_ids.ids,
            "allowed", "ALL" if allowed is None else len(allowed),
            "hr_mgr", x.has_group("hr.group_hr_manager"),
        )
