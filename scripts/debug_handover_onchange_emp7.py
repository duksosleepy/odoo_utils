# -*- coding: utf-8 -*-
import sys
from datetime import date, datetime, time

from odoo import Command

sys.stdout.reconfigure(encoding="utf-8")

user = env["res.users"].browse(61)
emp56 = user.sudo().employee_id
emp7 = env["hr.employee"].sudo().browse(7)
print("user:", user.login, "emp:", emp56.id, emp56.name, "mien:", emp56.mien)
print("emp7:", emp7.name if emp7.exists() else "MISSING", "mien:", emp7.mien, "dept:", emp7.department_id.name)

Leave = env["hr.leave"].with_user(user)
leave_type = env["hr.leave.type"].search([("name", "ilike", "Nghỉ phép (P)")], limit=1)
overlap_day = date(2026, 7, 15)
start_dt = datetime.combine(overlap_day, time(7, 0))
end_dt = datetime.combine(overlap_day, time(19, 0))

values = {
    "employee_id": emp56.id,
    "holiday_status_id": leave_type.id,
    "request_date_from": overlap_day.isoformat(),
    "request_date_to": overlap_day.isoformat(),
    "date_from": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
    "date_to": end_dt.strftime("%Y-%m-%d %H:%M:%S"),
    "handover_acceptance_ids": [
        Command.create({"employee_id": emp7.id, "handover_work_content": "test"}),
    ],
}
field_names = ["handover_acceptance_ids"]
fields_spec = {
    "handover_acceptance_ids": {
        "fields": {
            "sequence": {},
            "employee_id": {"fields": {"display_name": {}}},
            "handover_work_content": {},
        }
    },
    "handover_employee_ids": {"fields": {"display_name": {}}},
    "unavailable_handover_employee_ids": {"fields": {"display_name": {}}},
    "handover_recipient_list_readonly": {},
    "can_skip_work_handover": {},
    "skip_work_handover": {},
}

print("\n--- unavailable_handover compute ---")
try:
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
    unavail = draft.unavailable_handover_employee_ids
    print("unavailable ids:", unavail.ids)
    print("unavailable names:", unavail.mapped("name"))
except Exception as ex:
    print("unavailable compute FAIL:", type(ex).__name__, ex)

print("\n--- onchange handover_acceptance_ids ---")
try:
    result = Leave.onchange(values, field_names, fields_spec)
    print("onchange OK")
    lines = result.get("value", {}).get("handover_acceptance_ids") or []
    print("lines count:", len(lines))
except Exception as ex:
    print("onchange FAIL:", type(ex).__name__, ex)

print("\n--- web_read new leave spec ---")
try:
    draft = Leave.new(values)
    spec = fields_spec.copy()
    data = draft.web_read(spec)
    print("web_read OK", data[0].get("handover_acceptance_ids"))
except Exception as ex:
    print("web_read FAIL:", type(ex).__name__, ex)

print("\n--- employee web_search_read (many2one dropdown) ---")
domain = [
    ("id", "!=", emp56.id),
    ("user_id", "!=", False),
]
try:
    sr = env["hr.employee"].with_user(user).web_search_read(
        domain,
        {"display_name": {}},
        limit=5,
    )
    print("hr.employee search count:", sr.get("length", len(sr.get("records", []))))
except Exception as ex:
    print("hr.employee search FAIL:", type(ex).__name__, ex)

try:
    sr = env["hr.employee.public"].with_user(user).web_search_read(
        domain,
        {"display_name": {}},
        limit=5,
    )
    print("hr.employee.public search count:", sr.get("length", len(sr.get("records", []))))
    ids = [r["id"] for r in sr.get("records", [])]
    print("first ids:", ids[:10], "emp7 in results:", 7 in ids)
except Exception as ex:
    print("hr.employee.public search FAIL:", type(ex).__name__, ex)
