# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u = env["res.users"].sudo().browse(58)
print("=== USER 58 admin.lug ===")
print("login", u.login)
print("enforced", u._lug_permission_is_enforced())
print("lug_data_scope", u.lug_data_scope)
print("visibility_policy", u.visibility_policy)
print("employee_mien", u.employee_mien)
print("edit_policy", u.lug_hr_employee_edit_policy)
print("edit_zones", u.lug_hr_employee_edit_mien_zone_ids.mapped("legacy_mien"))
print("hr_user", u.has_group("hr.group_hr_user"))
print("edit_allowed", u.has_group("hr_employee_self_only.group_hr_employee_edit_allowed"))

mixin = env["hr.employee.access.mixin"]
domain = mixin._hr_employee_visibility_read_domain(u, model_name="hr.employee.public")
print("visibility domain", domain)

UserPub = env["hr.employee.public"].with_user(u)
Emp = env["hr.employee"].with_user(u)
print("public search", UserPub.search_count([]))
print("employee search", Emp.search_count([]))
print("Nam", UserPub.search_count([("mien", "=", "Nam")]))
print("VP", UserPub.search_count([("mien", "=", "VP")]))

# Sample employees in Nam
for eid in UserPub.search([("mien", "=", "Nam")], limit=3).ids:
    try:
        UserPub.browse(eid).check_access("read")
        Emp.browse(eid).check_access("read")
        emp = Emp.browse(eid)
        print("emp", eid, "read OK", "edit_allowed", emp._lug_is_employee_profile_edit_allowed())
    except Exception as ex:
        print("emp", eid, "FAIL", type(ex).__name__, str(ex)[:100])

# Try write simulation
nam = Emp.search([("mien", "=", "Nam")], limit=1)
if nam:
    try:
        nam.check_access("write")
        print("write check", nam.id, "OK")
    except Exception as ex:
        print("write check FAIL", str(ex)[:150])

# Test parent/ref access after restricted
UserPub.browse(nam.id if nam else 58)._hr_employee_read_is_restricted()
own = u.employee_id
print("own parent after restricted", own.parent_id.id if own.parent_id else False)
try:
    UserPub.browse(58).check_access("read")
except Exception as ex:
    print("read self public FAIL", str(ex)[:120])
