# -*- coding: utf-8 -*-
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

Employee = env["hr.employee"]
start = datetime(2026, 1, 1)
end = datetime(2026, 12, 31, 23, 59, 59)

for label, domain in [
    ("Phuong Nam", [("name", "ilike", "Phương"), ("mien", "=", "Nam")]),
    ("VP sample", [("mien", "=", "VP")]),
]:
    emp = Employee.search(domain, limit=1)
    if not emp:
        print(f"{label}: employee not found")
        continue
    ph = emp._get_public_holidays(start, end)
    scopes = set(ph.mapped("holiday_scope"))
    print(f"{label} | {emp.name} | mien={emp.mien!r} | count={len(ph)} | scopes={scopes}")
    for h in ph[:5]:
        print(f"  - {h.name} | scope={h.holiday_scope}")
