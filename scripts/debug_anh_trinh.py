# -*- coding: utf-8 -*-
Users = env["res.users"].sudo()
u = Users.search([("login", "ilike", "anh.trinh")], limit=1)
if not u:
    print("NOT FOUND")
else:
    allowed = u.lug_allowed_employee_edit_legacy_miens()
    print("login", u.login.encode("unicode_escape").decode())
    print("policy", u.lug_hr_employee_edit_policy)
    print("zones", [(z.id, (z.legacy_mien or "").encode("unicode_escape").decode()) for z in u.lug_hr_employee_edit_mien_zone_ids])
    print("allowed", "ALL" if allowed is None else sorted(allowed))
    print("groups", [g.name for g in u.groups_id if "HR" in g.name or "hr" in g.name.lower()][:10])
    print("lug_enforced", u._lug_permission_is_enforced())
    print("employee_id", u.employee_id.id if u.employee_id else None)

Employee = env["hr.employee"].with_user(u)
for eid in [2, 10, 4]:
    e = Employee.browse(eid)
    if not e.exists():
        continue
    print(
        "emp", eid,
        "legacy", repr(e._lug_employee_legacy_mien()),
        "allowed", e._lug_is_employee_profile_edit_allowed(),
        "readonly_ui", e.employee_form_force_readonly_ui,
    )
    try:
        with env.cr.savepoint():
            e.write({"ghi_chu": e.ghi_chu or "x"})
            print("  write OK")
    except Exception as ex:
        print("  write BLOCKED", type(ex).__name__)
