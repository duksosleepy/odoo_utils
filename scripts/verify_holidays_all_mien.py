# -*- coding: utf-8 -*-
from datetime import datetime

Employee = env["hr.employee"]
Leaves = env["resource.calendar.leaves"]
start = datetime(2026, 1, 1)
end = datetime(2026, 12, 31, 23, 59, 59)

all_holidays = Leaves.sudo().search([
    ("resource_id", "=", False),
    ("date_from", "<=", end),
    ("date_to", ">=", start),
])
print(f"Total public holidays 2026: {len(all_holidays)}")
for h in all_holidays:
    print(f"  - {h.name} | scope={getattr(h, 'holiday_scope', 'n/a')}")

store = Employee.search([("mien", "in", ["Bắc", "Nam", "ĐTT"])], limit=3)
vp = Employee.search([("mien", "=", "VP")], limit=1)
for label, emps in [("STORE", store), ("VP", vp)]:
    for e in emps:
        ph = e._get_public_holidays(start, end)
        print(f"{label} {e.name} mien={e.mien!r} holidays={len(ph)}")
