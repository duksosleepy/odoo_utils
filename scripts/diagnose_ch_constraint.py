# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

mod = env["ir.module.module"].search([("name", "=", "hr_public_holiday_mien")], limit=1)
print("module version:", mod.latest_version)

Leaves = env["resource.calendar.leaves"].sudo()
for h in Leaves.search([("resource_id", "=", False)]):
    print(f"id={h.id} scope={h.holiday_scope} {h.date_from.date()}..{h.date_to.date()} | {h.name}")

# Test constraint method
cls = env.registry["resource.calendar.leaves"]
methods = [m for m in cls._constraint_methods if "date_from" in getattr(m, "_constrains", ())]
print("constraint methods:", [m.__name__ for m in methods])

try:
    env["resource.calendar.leaves"].create({
        "name": "CH overlap test",
        "date_from": "2026-01-01 00:00:00",
        "date_to": "2026-06-29 23:59:59",
        "resource_id": False,
        "calendar_id": False,
        "company_id": env.company.id,
        "holiday_scope": "ch",
    })
    print("CREATE ch OK")
except Exception as e:
    print("CREATE ch FAIL:", e)
