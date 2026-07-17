# -*- coding: utf-8 -*-
import sys
from datetime import date, datetime, time
from odoo import Command

sys.stdout.reconfigure(encoding="utf-8")

user = env["res.users"].browse(61)
emp56 = user.sudo().employee_id
Leave = env["hr.leave"].with_user(user)
leave_type = env["hr.leave.type"].search([("name", "ilike", "Nghỉ phép (P)")], limit=1)
overlap_day = date(2026, 6, 29)
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

print("1) compute unavailable")
try:
    draft._compute_unavailable_handover_employee_ids()
    print("   ids:", draft.unavailable_handover_employee_ids.ids)
except Exception as ex:
    print("   FAIL", type(ex).__name__, ex)

print("2) read ids after compute")
try:
    print("   ids:", draft.unavailable_handover_employee_ids.ids)
except Exception as ex:
    print("   FAIL", type(ex).__name__, ex)

print("3) read mapped name")
try:
    print("   names:", draft.unavailable_handover_employee_ids.mapped("name"))
except Exception as ex:
    print("   FAIL", type(ex).__name__, ex)

print("4) onchange select handover on same date")
visible_id = env["hr.employee"].with_user(user).search(
    [("id", "!=", emp56.id), ("user_id", "!=", False)], limit=1
).id
values = {
    "employee_id": emp56.id,
    "holiday_status_id": leave_type.id,
    "request_date_from": overlap_day.isoformat(),
    "request_date_to": overlap_day.isoformat(),
    "date_from": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
    "date_to": end_dt.strftime("%Y-%m-%d %H:%M:%S"),
    "handover_acceptance_ids": [
        Command.create({"employee_id": visible_id, "handover_work_content": "x"}),
    ],
}
fields_spec = {
    "handover_acceptance_ids": {
        "fields": {
            "employee_id": {"fields": {"display_name": {}}},
            "handover_work_content": {},
        }
    },
    "unavailable_handover_employee_ids": {"fields": {"display_name": {}}},
    "handover_employee_ids": {"fields": {"display_name": {}}},
}
try:
    Leave.onchange(values, ["handover_acceptance_ids"], fields_spec)
    print("   OK")
except Exception as ex:
    print("   FAIL", type(ex).__name__, ex)

print("5) web_read draft with unavailable in spec")
try:
    data = draft.web_read(fields_spec)
    print("   OK unavailable:", data[0].get("unavailable_handover_employee_ids"))
except Exception as ex:
    print("   FAIL", type(ex).__name__, ex)
