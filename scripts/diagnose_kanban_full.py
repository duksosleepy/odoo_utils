# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u = env["res.users"].browse(85)
UserPub = env["hr.employee.public"].with_user(u)

# Get kanban view arch fields
view = env.ref("hr.hr_employee_public_view_kanban", raise_if_not_found=False)
if view:
    print("kanban arch snippet:", view.arch[:500])

# Simulate list load like web client
try:
    result = UserPub.web_search_read(
        [],
        {
            "id": {},
            "display_name": {},
            "name": {},
            "job_title": {},
            "work_phone": {},
            "work_email": {},
            "department_id": {"fields": {"display_name": {}}},
            "parent_id": {"fields": {"display_name": {}}},
            "avatar_128": {},
            "mien": {},
        },
        limit=80,
    )
    records = result.get("records", result) if isinstance(result, dict) else result
    print("web_search_read count", len(records))
    for rec in records[:5]:
        print(" ", rec.get("id"), rec.get("display_name"), "parent", rec.get("parent_id"))
except Exception as e:
    print("web_search_read FAIL", type(e).__name__, str(e)[:300])

# Try read all visible with parent_id
ids = UserPub.search([]).ids
print("search ids", ids)
try:
    rows = UserPub.browse(ids).read(["name", "parent_id", "department_id"])
    print("read all OK", len(rows))
    for r in rows:
        if r.get("parent_id"):
            print(" parent ref", r["id"], "->", r["parent_id"])
except Exception as e:
    print("read all FAIL", type(e).__name__, str(e)[:300])

# web_read all
try:
    data = UserPub.browse(ids).web_read({
        "display_name": {},
        "parent_id": {"fields": {"display_name": {}}},
        "department_id": {"fields": {"display_name": {}}},
    })
    print("web_read all OK", len(data))
except Exception as e:
    print("web_read all FAIL", type(e).__name__, str(e)[:300])
