# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u = env["res.users"].sudo().browse(85)
print("=== USER 85 ===")
print("login", u.login)
print("enforced", u._lug_permission_is_enforced())
print("lug_data_scope", u.lug_data_scope)
print("visibility_policy", u.visibility_policy)
print("employee_mien", u.employee_mien)
print("employee_id", u.employee_id.id)
print("edit_policy", u.lug_hr_employee_edit_policy)
print("edit_zones", u.lug_hr_employee_edit_mien_zone_ids.mapped("legacy_mien"))
print("groups hr_user", u.has_group("hr.group_hr_user"))
print("groups staff", u.has_group("hr_employee_hrm_detail.group_hr_employees_staff"))

mixin = env["hr.employee.access.mixin"]
domain = mixin._hr_employee_visibility_read_domain(u, model_name="hr.employee.public")
print("visibility domain", domain)

UserPub = env["hr.employee.public"].with_user(u)
print("total search", UserPub.search_count([]))
print("VP count", UserPub.search_count([("mien", "=", "VP")]))
print("Nam count", UserPub.search_count([("mien", "=", "Nam")]))

# Kanban simulation
try:
    data = UserPub.web_search_read([], {"display_name": {}}, limit=5)
    print("web_search_read OK", len(data.get("records", data) if isinstance(data, dict) else data))
except Exception as e:
    print("web_search_read FAIL", type(e).__name__, str(e)[:200])

# Check access on batch
ids = UserPub.search([], limit=10).ids
print("first ids", ids)
try:
    UserPub.browse(ids).check_access("read")
    print("batch check_access OK")
except Exception as e:
    print("batch check_access FAIL", type(e).__name__, str(e)[:200])

# Employee 44 specifically
try:
    UserPub.browse(44).check_access("read")
    print("emp44 check_access OK")
except Exception as e:
    print("emp44 check_access FAIL", type(e).__name__, str(e)[:200])

# _check_access return
r = UserPub.browse(44)
result = r._check_access("read")
print("_check_access(44) returns", result)
