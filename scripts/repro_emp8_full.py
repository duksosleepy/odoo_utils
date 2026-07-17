# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
Pub = env["hr.employee.public"].with_user(u85)

def build_spec_from_view(emp_id):
    views = env["ir.ui.view"].sudo().search([
        ("model", "=", "hr.employee.public"),
        ("type", "=", "form"),
    ])
    # use main form
    view = env.ref("hr.hr_employee_public_view_form", raise_if_not_found=False)
    if not view:
        view = views[0] if views else None
    arch = view.arch_db if view else ""
    Model = env["hr.employee.public"]
    spec = {"id": {}}
    for fname, field in Model._fields.items():
        if field.type in ("one2many",):
            continue
        if field.groups and not u85.has_groups(field.groups):
            continue
        spec[fname] = {}
    return spec

for eid in [8, 71]:
    e = env["hr.employee"].sudo().browse(eid)
    print(f"\n=== emp {eid} {e.name} parent={e.parent_id.id} coach={e.coach_id.id} ===")
    spec = build_spec_from_view(eid)
    print("spec fields", len(spec))
    try:
        r = Pub.browse(eid).web_read(spec)
        print("full web_read OK", len(r[0]) if r else 0, "keys")
    except Exception as ex:
        print("full web_read FAIL", type(ex).__name__, str(ex)[:300])

# open via res.users form
u13 = env["res.users"].sudo().browse(13)
print("\n=== open user 13 trang.cao ===")
try:
    u13.with_user(u85).web_read({"name": {}, "employee_id": {"fields": {"display_name": {}, "name": {}}}})
    print("user web_read OK")
except Exception as ex:
    print("user web_read FAIL", ex)

# MRO
print("\nMRO _check_access:", [c.__name__ for c in type(env["hr.employee.public"]).mro() if '_check_access' in c.__dict__ or 'HrEmployeePublic' in c.__name__ or 'Lug' in c.__name__][:8])

# module version
mod = env["ir.module.module"].sudo().search([("name", "=", "lug_permission")])
print("lug_permission state", mod.state, "version", mod.latest_version)
