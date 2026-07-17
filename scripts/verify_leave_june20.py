# -*- coding: utf-8 -*-
from datetime import datetime

Leave = env["hr.leave"]
leaves = Leave.search(
    [
        ("date_from", ">=", "2026-06-20"),
        ("date_from", "<", "2026-06-21"),
    ],
    limit=10,
)
for lv in leaves:
    emp = lv.employee_id
    print(
        "leave", lv.id,
        "emp", emp.id,
        "mien", repr(emp._employee_schedule_mien()),
        "days", lv.number_of_days,
        "state", lv.state,
    )
    if emp._uses_store_full_week_schedule():
        durations = lv._get_durations()
        print("  recomputed durations:", durations)
