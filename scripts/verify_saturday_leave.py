# -*- coding: utf-8 -*-
from datetime import date

Employee = env["hr.employee"]
nhi = Employee.search([("name", "ilike", "Nhi")], limit=5)
for e in nhi:
    print("emp", e.id, "mien", repr(e._employee_schedule_mien()), "cal", e.version_id.resource_calendar_id.id)
    unusual = e._get_unusual_days(date(2026, 6, 20), date(2026, 6, 20))
    print("  unusual 2026-06-20:", unusual)
    days = e._get_work_days_data_batch(
        date(2026, 6, 20), date(2026, 6, 20), compute_leaves=True
    )
    print("  work days:", days)
