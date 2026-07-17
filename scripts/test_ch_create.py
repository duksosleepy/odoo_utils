# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
try:
    rec = env["resource.calendar.leaves"].create({
        "name": "CH test",
        "date_from": "2026-01-01 00:00:00",
        "date_to": "2026-06-29 23:59:59",
        "resource_id": False,
        "calendar_id": False,
        "company_id": env.company.id,
        "holiday_scope": "ch",
    })
    print("CREATE OK id=", rec.id)
    rec.unlink()
except Exception as e:
    print("CREATE FAIL:", type(e).__name__, e)
