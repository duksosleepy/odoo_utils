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

# proposed fix: compute on contextualized recordset
draft_ctx = draft._with_handover_employee_read_context()
draft_ctx._compute_unavailable_handover_employee_ids()

print("read unavailable on contextualized draft:")
print(" ids:", draft_ctx.unavailable_handover_employee_ids.ids)
print(" names:", draft_ctx.unavailable_handover_employee_ids.mapped("name"))

print("\nread unavailable on plain draft (same record):")
try:
    print(" ids:", draft.unavailable_handover_employee_ids.ids)
    print(" names:", draft.unavailable_handover_employee_ids.mapped("name"))
except Exception as ex:
    print(" FAIL:", type(ex).__name__, ex)
