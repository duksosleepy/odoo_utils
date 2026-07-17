# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

u = env["res.users"].browse(85)
errors = []

# 1. mail activity groups (original crash path)
try:
    groups = u._get_activity_groups()
    print("activity_groups OK", len(groups))
except Exception as ex:
    errors.append(("activity_groups", type(ex).__name__, str(ex)[:200]))
    print("activity_groups FAIL", type(ex).__name__, str(ex)[:200])

# 2. session lug_ui
print("lug_ui", u._lug_ui_systray_flags())

# 3. time off overview - hr.leave.report.calendar
try:
    Cal = env["hr.leave.report.calendar"].with_user(u)
    cnt = Cal.search_count([])
    print("leave calendar count", cnt)
    if cnt:
        rec = Cal.search([], limit=1)
        rec.read(["name", "employee_id"])
        print("calendar read OK")
except Exception as ex:
    errors.append(("calendar", type(ex).__name__, str(ex)[:200]))
    print("calendar FAIL", type(ex).__name__, str(ex)[:200])

# 4. hr.leave overview
try:
    Leave = env["hr.leave"].with_user(u)
    print("leave count", Leave.search_count([]))
    leaves = Leave.search([], limit=3)
    if leaves:
        leaves.web_read({"employee_id": {"fields": {"display_name": {}}}, "state": {}})
        print("leave web_read OK")
except Exception as ex:
    errors.append(("leave_web_read", type(ex).__name__, str(ex)[:200]))
    print("leave web_read FAIL", type(ex).__name__, str(ex)[:200])

# 5. discuss channels
try:
    ch = env["discuss.channel"].with_user(u).search([], limit=3)
    print("channels", len(ch))
except Exception as ex:
    errors.append(("channels", type(ex).__name__, str(ex)[:200]))
    print("channels FAIL", type(ex).__name__, str(ex)[:200])

# 6. lug leave rule domain
rule = env.ref("lug_permission.hr_leave_lug_scope_rule", raise_if_not_found=False)
if rule:
    try:
        dom = rule.with_user(u)._compute_domain("hr.leave", "read")
        print("lug leave rule domain OK", dom)
    except Exception as ex:
        errors.append(("lug_rule", type(ex).__name__, str(ex)[:200]))
        print("lug rule FAIL", type(ex).__name__, str(ex)[:200])

print("errors", errors)
