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

print("ctx on draft:", draft.env.context.get("_allow_read_hr_employee"))

ctx_draft = draft._with_handover_employee_read_context()
print("ctx on wrapped:", ctx_draft.env.context.get("_allow_read_hr_employee"))

print("\ncompute on plain draft:")
try:
    draft._compute_unavailable_handover_employee_ids()
    print(" OK")
except Exception as ex:
    print(" FAIL", type(ex).__name__, ex)

print("\ncompute on wrapped draft:")
try:
    ctx_draft._compute_unavailable_handover_employee_ids()
    print(" OK ids", ctx_draft.unavailable_handover_employee_ids.ids)
except Exception as ex:
    print(" FAIL", type(ex).__name__, ex)

# simulate ORM triggering compute via field access on wrapped vs plain
print("\naccess field on plain:")
try:
    print(draft.unavailable_handover_employee_ids.ids)
except Exception as ex:
    print(" FAIL", type(ex).__name__, ex)

print("\naccess field on wrapped:")
try:
    print(ctx_draft.unavailable_handover_employee_ids.ids)
except Exception as ex:
    print(" FAIL", type(ex).__name__, ex)
