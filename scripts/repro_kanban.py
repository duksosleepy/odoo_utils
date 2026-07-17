# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
Pub = env["hr.employee.public"].with_user(u85)
Emp = env["hr.employee"].with_user(u85)

# kanban load like UI
spec = {
    "display_name": {},
    "job_title": {},
    "parent_id": {"fields": {"display_name": {}}},
    "coach_id": {"fields": {"display_name": {}}},
    "department_id": {"fields": {"display_name": {}}},
    "attendance_state": {},
    "activity_state": {},
}
for model_name, M in [("public", Pub), ("employee", Emp)]:
    try:
        rows, total = M.web_search_read([], spec, limit=80)
        ids = [r["id"] for r in rows]
        print(model_name, "total", total, "has8", 8 in ids, "has71", 71 in ids)
    except Exception as ex:
        print(model_name, "kanban FAIL", str(ex)[:300])

# Direct open after kanban - sometimes uses read([ids])
try:
    Pub.browse(8).read(["name", "parent_id", "coach_id", "department_id"])
    print("read() OK")
except Exception as ex:
    print("read() FAIL", ex)

# Test WITHOUT lug enforced - simulate misconfigured user
u = u85.sudo()
print("lug_groups", u.lug_group_ids.mapped("name"))
print("enforced", u._lug_permission_is_enforced())
