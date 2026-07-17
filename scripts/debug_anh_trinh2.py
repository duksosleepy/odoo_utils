# -*- coding: utf-8 -*-
u = env["res.users"].sudo().search([("login", "=", "anh.trinh@sangtam.com")], limit=1)
print("edit_allowed", u.has_group("hr_employee_self_only.group_hr_employee_edit_allowed"))
print("hr_user", u.has_group("hr.group_hr_user"))
print("hr_manager", u.has_group("hr.group_hr_manager"))
print("view_personal", u.has_group("hr_employee_self_only.group_hr_employee_view_personal_allowed"))

perm = u._lug_effective_permission_map()
print("lug hr perms", perm.get("hr", set()))

Employee = env["hr.employee"].with_user(u)
vp = env["hr.employee"].sudo().search([("mien", "=", "VP")], limit=1)
e = Employee.browse(vp.id)
print("vp id", vp.id, "legacy", repr(e._lug_employee_legacy_mien()))
print("lug allowed edit", e._lug_is_employee_profile_edit_allowed())
print("readonly_ui", e.employee_form_force_readonly_ui)

try:
    with env.cr.savepoint():
        e.write({"ghi_chu": "test"})
        print("write OK")
except Exception as ex:
    print("write FAIL", type(ex).__name__, str(ex)[:100].encode("unicode_escape").decode())
