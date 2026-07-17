# -*- coding: utf-8 -*-
import sys
from datetime import timedelta
from odoo import fields
from odoo.exceptions import UserError

sys.stdout.reconfigure(encoding="utf-8")

user = env["res.users"].browse(61)
emp = env["hr.employee"].browse(56)
start = fields.Date.today() + timedelta(days=30)

# simulate admin-created leave with validation=both (bypass mien via sudo on wrong type)
for type_id, label in [(86, "both"), (75, "multi_step P")]:
    print(f"\n=== test type {type_id} {label} ===")
    try:
        with env.cr.savepoint():
            leave = env["hr.leave"].sudo().create({
                "name": "diag",
                "employee_id": emp.id,
                "holiday_status_id": type_id,
                "request_date_from": start,
                "request_date_to": start,
                "date_from": fields.Datetime.to_datetime(start),
                "date_to": fields.Datetime.to_datetime(start + timedelta(days=1)),
            })
            print("created state", leave.state, "validation", leave.validation_type)
            try:
                leave.with_user(user).action_approve()
                print("action_approve OK")
            except UserError as ex:
                print("action_approve UserError:", ex)
            except Exception as ex:
                print("action_approve other:", type(ex).__name__, ex)
    except Exception as ex:
        print("create failed:", ex)
