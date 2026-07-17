# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

u = env["res.users"].browse(85)
env = env(user=u.id)

print("user", u.login, "lug_enforced", u._lug_permission_is_enforced())
print("employee_mien", u.employee_mien, "scope", u.lug_data_scope)

# Calendar (overview backend)
Cal = env["hr.leave.report.calendar"]
print("calendar search", Cal.search_count([]))

# Dashboard action / employee stats on overview
for model in [
    "hr.leave",
    "hr.leave.report.calendar",
    "hr.employee",
    "hr.employee.public",
]:
    M = env[model]
    try:
        print(model, "search_count", M.search_count([]))
    except Exception as ex:
        print(model, "search_count FAIL", type(ex).__name__, str(ex)[:100])

# Employee 51
print("emp51 public readable", end=" ")
try:
    env["hr.employee.public"].browse(51).check_access("read")
    print("yes")
except Exception as ex:
    print("no", type(ex).__name__)

# Simulate overview RPCs - get_unusual_days, search_read on calendar
try:
    days = Cal.get_unusual_days("2026-01-01", "2026-12-31")
    print("unusual_days OK", len(days))
except Exception as ex:
    print("unusual_days FAIL", type(ex).__name__, str(ex)[:150])

try:
    data = Cal.search_read([], ["name", "start_datetime", "stop_datetime", "employee_id"])
    print("calendar search_read", len(data))
except Exception as ex:
    print("calendar search_read FAIL", type(ex).__name__, str(ex)[:150])

# hr_holidays dashboard - leave summary for employee
emp = u.employee_id
if emp:
    try:
        summary = env["hr.leave.type"].with_user(u).get_allocation_data(emp.ids)
        print("allocation_data OK")
    except Exception as ex:
        print("allocation_data FAIL", type(ex).__name__, str(ex)[:150])
    try:
        leaves = env["hr.leave"].search([("employee_id", "=", emp.id)])
        print("own leaves", len(leaves))
    except Exception as ex:
        print("own leaves FAIL", ex)

# Check if employee_id 51 appears in any accessible leave/calendar via sudo leak
for lid in env["hr.leave"].sudo().search([]).ids:
    lv = env["hr.leave"].sudo().browse(lid)
    if lv.employee_id.id == 51:
        try:
            env["hr.leave"].browse(lid).read(["name"])
            print("leave", lid, "readable by user")
        except Exception:
            print("leave", lid, "NOT readable (good)")
