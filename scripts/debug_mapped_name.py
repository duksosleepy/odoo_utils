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

draft._compute_unavailable_handover_employee_ids()
print("after compute, ids:", draft.unavailable_handover_employee_ids.ids)
try:
    print("names:", draft.unavailable_handover_employee_ids.mapped("name"))
except Exception as ex:
    print("names FAIL:", type(ex).__name__, ex)

# availability onchange path
visible_id = env["hr.employee"].with_user(user).search(
    [("id", "!=", emp56.id), ("user_id", "!=", False)], limit=1
).id
draft.handover_employee_ids = [(6, 0, [visible_id])]
try:
    unavail = draft._get_unavailable_handover_employees()
    print("_get_unavailable names:", unavail.mapped("name"))
except Exception as ex:
    print("_get_unavailable FAIL:", type(ex).__name__, ex)

try:
    draft._onchange_handover_employee_availability()
    print("_onchange_handover_employee_availability OK")
except Exception as ex:
    print("_onchange_handover_employee_availability FAIL:", type(ex).__name__, ex)
