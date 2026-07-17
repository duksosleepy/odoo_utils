# -*- coding: utf-8 -*-
import sys
from datetime import date, datetime, time

sys.stdout.reconfigure(encoding="utf-8")

user = env["res.users"].browse(61)
emp56 = user.sudo().employee_id
Leave = env["hr.leave"].with_user(user)
leave_type = env["hr.leave.type"].search([("name", "ilike", "Nghỉ phép (P)")], limit=1)

# find leaves involving emp 7
leaves7 = env["hr.leave"].sudo().search([("employee_id", "=", 7), ("state", "in", ("confirm", "validate1", "validate"))])
print("emp7 active leaves:", len(leaves7))
for lv in leaves7[:5]:
    print(" ", lv.id, lv.request_date_from, lv.request_date_to, lv.state)

# test dates from screenshot - calendar 2026, user creating new leave
for overlap_day in (date(2026, 6, 29), date(2026, 6, 30), date(2026, 7, 1)):
    start_dt = datetime.combine(overlap_day, time(7, 0))
    end_dt = datetime.combine(overlap_day, time(19, 0))
    draft = Leave.new(
        {
            "employee_id": emp56.id,
            "holiday_status_id": leave_type.id,
            "request_date_from": overlap_day,
            "request_date_to": overlap_day,
            "date_from": start_dt,
            "date_to": end_dt,
        }
    )
    try:
        draft._compute_unavailable_handover_employee_ids()
        unavail = draft.unavailable_handover_employee_ids
        print(f"\n{overlap_day}: unavailable={unavail.ids}")
        if unavail:
            print("  names via field:", unavail.mapped("name"))
    except Exception as ex:
        print(f"{overlap_day}: compute FAIL", type(ex).__name__, ex)

    fields_spec = {
        "unavailable_handover_employee_ids": {"fields": {"display_name": {}}},
        "handover_acceptance_ids": {
            "fields": {
                "employee_id": {"fields": {"display_name": {}}},
            }
        },
    }
    values = {
        "employee_id": emp56.id,
        "holiday_status_id": leave_type.id,
        "request_date_from": overlap_day.isoformat(),
        "request_date_to": overlap_day.isoformat(),
        "date_from": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "date_to": end_dt.strftime("%Y-%m-%d %H:%M:%S"),
    }
    try:
        Leave.onchange(values, ["request_date_from"], fields_spec)
        print(f"  onchange request_date OK")
    except Exception as ex:
        print(f"  onchange request_date FAIL", type(ex).__name__, ex)

# web_read emp7 without context - what does it return?
rec = env["hr.employee"].with_user(user).browse(7)
try:
    data = rec.web_read({"display_name": {}})
    print("\nweb_read emp7 data:", data)
except Exception as ex:
    print("\nweb_read emp7 FAIL:", type(ex).__name__, ex)
