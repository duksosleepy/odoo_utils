# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Apply defaults + upgrade hooks
env["res.users"]._lug_set_default_employee_edit_scopes()
u = env["res.users"].sudo().browse(85)
print("=== AFTER DEFAULTS ===")
print("lug_data_scope", u.lug_data_scope)
print("visibility_policy", u.visibility_policy)
print("employee_mien", u.employee_mien)

UserPub = env["hr.employee.public"].with_user(u)
print("VP visible", UserPub.search_count([("mien", "=", "VP")]))
print("Nam visible", UserPub.search_count([("mien", "=", "Nam")]))

# Poison cache then test access (kanban open path)
UserPub.browse(81)._hr_employee_read_is_restricted()
print("parent after restricted", u.employee_id.parent_id.id)

try:
    UserPub.browse(44).check_access("read")
    print("check_access 44 OK")
except Exception as e:
    print("check_access 44 FAIL", str(e)[:120])

try:
    data = UserPub.web_search_read([], {"display_name": {}, "parent_id": {"fields": {"display_name": {}}}}, limit=80)
    recs = data.get("records", data)
    print("kanban web_search_read OK", len(recs))
except Exception as e:
    print("kanban FAIL", str(e)[:200])

ids = UserPub.search([]).ids
try:
    UserPub.browse(ids).check_access("read")
    print("batch check_access OK", len(ids))
except Exception as e:
    print("batch FAIL", str(e)[:200])
