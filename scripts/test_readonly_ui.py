# -*- coding: utf-8 -*-
user = env["res.users"].sudo().search([("login", "=", "admin.lug@sangtam.com")], limit=1)
Employee = env["hr.employee"].with_user(user)
for eid in [10, 2, 4]:
    e = Employee.browse(eid)
    print(
        "emp", eid,
        "legacy", repr(e._lug_employee_legacy_mien()),
        "allowed", e._lug_is_employee_profile_edit_allowed(),
        "readonly_ui", e.employee_form_force_readonly_ui,
    )
