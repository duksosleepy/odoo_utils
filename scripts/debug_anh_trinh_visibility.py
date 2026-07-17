# -*- coding: utf-8 -*-
u = env["res.users"].sudo().search([("login", "=", "anh.trinh@sangtam.com")], limit=1)
print("visibility_policy", u.visibility_policy)
print("lug_scope", u.lug_data_scope)
print("employee_mien", u.employee_mien)
print("lug_enforced", u._lug_permission_is_enforced())

EmployeeSudo = env["hr.employee"].sudo()
EmployeeUser = env["hr.employee"].with_user(u)

vp_all = EmployeeSudo.search([("mien", "=", "VP")])
vp_visible = EmployeeUser.search([("mien", "=", "VP")])
print("vp total", len(vp_all), "visible to user", len(vp_visible))

empty_mien = EmployeeSudo.search([("mien", "=", False)])
empty_visible = EmployeeUser.search([("mien", "=", False)])
print("empty mien total", len(empty_mien), "visible", len(empty_visible))

for e in vp_visible[:3]:
    eu = EmployeeUser.browse(e.id)
    print(
        "vp", e.id,
        "legacy", repr(eu._lug_employee_legacy_mien()),
        "allowed", eu._lug_is_employee_profile_edit_allowed(),
        "readonly", eu.employee_form_force_readonly_ui,
    )

for e in empty_visible[:3]:
    eu = EmployeeUser.browse(e.id)
    print(
        "empty", e.id,
        "legacy", repr(eu._lug_employee_legacy_mien()),
        "allowed", eu._lug_is_employee_profile_edit_allowed(),
        "readonly", eu.employee_form_force_readonly_ui,
    )
