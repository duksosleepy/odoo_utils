# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
Pub = env["hr.employee.public"].with_user(u85)
mixin = env["hr.employee.access.mixin"]
refs = set(mixin._hr_employee_access_reference_readable_ids(u85))
policy = mixin._hr_employee_policy_domain(u85)

def emp_m2o_fields(eid):
    e = env["hr.employee"].sudo().browse(eid)
    Model = env["hr.employee.public"]
    out = []
    for fname, field in Model._fields.items():
        if field.type != "many2one":
            continue
        if field.comodel_name not in ("hr.employee", "hr.employee.public"):
            continue
        val = getattr(e, fname, False)
        if val:
            vid = val.id if hasattr(val, 'id') else val
            in_policy = bool(env["hr.employee"].sudo().search_count([("id","=",vid)] + (list(policy) if policy else [])))
            out.append((fname, vid, val.display_name if hasattr(val,'display_name') else val, in_policy, vid in refs))
    return out

for eid in [8, 71]:
    e = env["hr.employee"].sudo().browse(eid)
    print(f"\n=== emp {eid} {e.name} ===")
    for row in emp_m2o_fields(eid):
        fname, vid, name, in_pol, in_ref = row
        flag = "OK" if in_pol or in_ref else "BAD"
        print(f"  {flag} {fname} -> {vid} {name} policy={in_pol} ref={in_ref}")

# Try web_read with each m2o individually
e8 = Pub.browse(8)
for fname, field in env["hr.employee.public"]._fields.items():
    if field.type == "many2one" and field.comodel_name in ("hr.employee", "hr.employee.public"):
        val = env["hr.employee"].sudo().browse(8)[fname]
        if not val:
            continue
        try:
            e8.web_read({fname: {"fields": {"display_name": {}}}})
        except Exception as ex:
            if "employee" in str(ex).lower() or "AccessError" in type(ex).__name__:
                print(f"FAIL on field {fname}: {str(ex)[:200]}")
