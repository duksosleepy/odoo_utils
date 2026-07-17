# -*- coding: utf-8 -*-
from datetime import datetime

Employee = env["hr.employee"]
nhi = Employee.search([("name", "ilike", "Cao Ngọc Nhi")], limit=1)
if not nhi:
    print("Employee not found")
else:
    e = nhi[0]
    mien = e._employee_schedule_mien() if hasattr(e, "_employee_schedule_mien") else e.mien
    start = datetime(2026, 1, 1)
    end = datetime(2026, 12, 31, 23, 59, 59)
    ph = e._get_public_holidays(start, end)
    print(f"Employee: {e.name} | mien={mien!r} | holidays={len(ph)}")
    for h in ph:
        print(
            f"  - {h.name} | scope={h.holiday_scope} | "
            f"{h.date_from.date()} -> {h.date_to.date()}"
        )
    data = env["hr.employee"].with_context(employee_id=e.id).get_special_days_data(
        "2026-01-01 00:00:00",
        "2026-12-31 23:59:59",
    )
    print(f"bankHolidays in sidebar: {len(data.get('bankHolidays', []))}")
