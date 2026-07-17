# -*- coding: utf-8 -*-
import sys
from datetime import timedelta
from odoo import fields
sys.stdout.reconfigure(encoding="utf-8")

start = fields.Date.today() + timedelta(days=30)
user = env["res.users"].sudo().search([("login", "=", "khan.nguyen@sangtam.com")], limit=1)
emp = user.employee_id
p = env["hr.leave.type"].browse(75)
allocs = env["hr.leave.allocation"].sudo().search([
    ("employee_id", "=", emp.id), ("holiday_status_id", "=", 75), ("state", "=", "validate")
])
print(f"khan.nguyen allocations: {len(allocs)} validate, days={allocs.number_of_days if allocs else 0}")
try:
    with env.cr.savepoint():
        lv = env["hr.leave"].with_user(user).with_context(
            skip_handover_submit_bot_notify=True,
            skip_responsible_submit_notify=True,
        ).create({
            "name": "verify after alloc",
            "employee_id": emp.id,
            "holiday_status_id": 75,
            "request_date_from": start,
            "request_date_to": start,
            "date_from": fields.Datetime.to_datetime(start),
            "date_to": fields.Datetime.to_datetime(start + timedelta(days=1)),
        })
    print(f"CREATE OK: leave type={lv.holiday_status_id.name} state={lv.state}")
except Exception as ex:
    print(f"CREATE FAIL: {ex}")

vp = env["hr.employee"].sudo().search([("active", "=", True), ("mien", "=", "VP")])
ok = 0
for e in vp:
    a = env["hr.leave.allocation"].sudo().search([
        ("employee_id", "=", e.id), ("holiday_status_id", "=", 75), ("state", "=", "validate")
    ], limit=1)
    if a:
        ok += 1
print(f"VP employees with validate P allocation: {ok}/{len(vp)}")
