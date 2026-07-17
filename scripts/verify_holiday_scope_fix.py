# -*- coding: utf-8 -*-
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

Leaves = env["resource.calendar.leaves"].sudo()
company = env.company.id

# Overlap with VP seed should succeed for CH scope
try:
    ch = Leaves.create(
        {
            "name": "tết CH test",
            "date_from": "2026-01-01 00:00:00",
            "date_to": "2026-06-30 23:59:59",
            "resource_id": False,
            "calendar_id": False,
            "company_id": company,
            "holiday_scope": "ch",
        }
    )
    print("CH create OK id=", ch.id)
    ch.unlink()
except Exception as e:
    print("CH create FAIL:", e)

nhi = env["hr.employee"].search([("mien", "=", "Nam")], limit=1)
if nhi:
    start = datetime(2026, 1, 1)
    end = datetime(2026, 12, 31, 23, 59, 59)
    ph = nhi._get_public_holidays(start, end)
    scopes = set(ph.mapped("holiday_scope"))
    print(f"Nam employee holidays={len(ph)} scopes={scopes}")
