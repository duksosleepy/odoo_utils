# -*- coding: utf-8 -*-
import sys
from datetime import date, datetime, time

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

overlapping = env["hr.leave"].sudo().search(
    [
        ("state", "in", ("confirm", "validate1", "validate")),
        ("date_from", "<", end_dt),
        ("date_to", ">", start_dt),
    ]
)
unavailable_ids = overlapping.mapped("employee_id").ids
print("unavailable_ids:", unavailable_ids)

ctx_draft = draft._with_handover_employee_read_context()
try:
    ctx_draft.unavailable_handover_employee_ids = ctx_draft._handover_employee_browse(unavailable_ids)
    print("contextualized assign OK, ids:", ctx_draft.unavailable_handover_employee_ids.ids)
    print("names:", ctx_draft.unavailable_handover_employee_ids.mapped("name"))
except Exception as ex:
    print("contextualized assign FAIL:", type(ex).__name__, ex)
