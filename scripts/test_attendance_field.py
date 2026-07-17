# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u = env["res.users"].browse(58)
print("attendance officer", u.has_group("hr_attendance.group_hr_attendance_officer"))
Pub = env["hr.employee.public"].with_user(u)
Emp = env["hr.employee"].with_user(u)

spec = {
    "display_name": {},
    "attendance_state": {},
    "name": {},
    "parent_id": {"fields": {"display_name": {}}},
}

try:
    data = Pub.web_search_read([], spec, limit=5)
    recs = data.get("records", data)
    print("public web_search_read OK", len(recs), "keys", list(recs[0].keys()) if recs else [])
    assert "attendance_state" not in (recs[0] if recs else {}), "attendance_state should be stripped"
except Exception as ex:
    print("public FAIL", str(ex)[:200])

try:
    data = Emp.web_search_read([], spec, limit=5)
    recs = data.get("records", data)
    print("employee web_search_read OK", len(recs))
except Exception as ex:
    print("employee FAIL", str(ex)[:200])
