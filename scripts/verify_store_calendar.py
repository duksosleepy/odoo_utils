# -*- coding: utf-8 -*-
from datetime import date

Employee = env["hr.employee"]
store = Employee.search([("mien", "in", ["Bắc", "Nam", "ĐTT"])], limit=5)
cal = env.ref("hr_public_holiday_mien.resource_calendar_store_full_week")
print("Calendar id:", cal.id, "work slots:", len(cal.attendance_ids.filtered(lambda a: a.day_period != "lunch")))
for e in store:
    mien = e._employee_schedule_mien()
    cal_name = e.version_id.resource_calendar_id.name if e.version_id else "N/A"
    ph = e._get_public_holidays(date(2026, 1, 1), date(2026, 12, 31))
    print(
        f"  id={e.id} mien={mien!r} cal_id={e.version_id.resource_calendar_id.id if e.version_id else None} "
        f"holidays={len(ph)} store={e._uses_store_full_week_schedule()}"
    )
nhi = Employee.search([("name", "ilike", "Cao Ngọc Nhi")], limit=1)
if nhi:
    e = nhi[0]
    print("Nhi id:", e.id, "mien:", repr(e._employee_schedule_mien()), "cal:", e.version_id.resource_calendar_id.id)
