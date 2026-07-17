# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

user = env["res.users"].browse(61)
emp56 = user.sudo().employee_id

for term in ("nhi", "Cao", "Nhi", "cao ngoc"):
    for model in ("hr.employee", "hr.employee.public"):
        M = env[model].with_user(user)
        found = M.name_search(term, limit=10)
        ids = [x[0] for x in found]
        print(f"{model} name_search '{term}':", ids, "emp7:", 7 in ids)

# direct read emp 7 as user 61
for model in ("hr.employee", "hr.employee.public"):
    try:
        rec = env[model].with_user(user).browse(7)
        rec.check_access("read")
        print(f"{model} browse(7) access OK")
        print("  name:", rec.name)
    except Exception as ex:
        print(f"{model} browse(7) FAIL:", type(ex).__name__, ex)

# with handover context
from odoo.addons.hr.models.hr_employee import _ALLOW_READ_HR_EMPLOYEE
try:
    rec = env["hr.employee"].with_user(user).with_context(
        _allow_read_hr_employee=_ALLOW_READ_HR_EMPLOYEE
    ).browse(7)
    print("hr.employee browse(7) handover ctx name:", rec.name)
except Exception as ex:
    print("handover ctx FAIL:", type(ex).__name__, ex)

# pick visible colleague and onchange
Leave = env["hr.leave"].with_user(user)
visible_id = env["hr.employee"].with_user(user).search(
    [("id", "!=", emp56.id), ("user_id", "!=", False)], limit=1
).id
print("visible colleague:", visible_id)

from odoo import Command
from datetime import date, datetime, time
overlap_day = date(2026, 7, 15)
start_dt = datetime.combine(overlap_day, time(7, 0))
end_dt = datetime.combine(overlap_day, time(19, 0))
leave_type = env["hr.leave.type"].search([("name", "ilike", "Nghỉ phép (P)")], limit=1)

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
}
try:
    Leave.onchange(values, ["handover_acceptance_ids"], fields_spec)
    print("onchange visible colleague OK")
except Exception as ex:
    print("onchange visible FAIL:", type(ex).__name__, ex)

# simulate many2one read RPC for emp 7 (what widget does after bad selection)
try:
    env["hr.employee"].with_user(user).browse(7).web_read({"display_name": {}})
    print("web_read emp7 OK")
except Exception as ex:
    print("web_read emp7 FAIL:", type(ex).__name__, ex)
