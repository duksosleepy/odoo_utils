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

draft._compute_unavailable_handover_employee_id_list()
print("unavailable ids:", draft.unavailable_handover_employee_id_list)
print("helper names:", draft._unavailable_handover_employees().mapped("name"))

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
    "unavailable_handover_employee_id_list": {},
}
Leave.onchange(values, ["handover_acceptance_ids"], fields_spec)
print("onchange handover selection: OK")
