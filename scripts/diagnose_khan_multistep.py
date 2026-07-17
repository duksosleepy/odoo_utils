# -*- coding: utf-8 -*-
import sys
from datetime import timedelta
from odoo import fields

sys.stdout.reconfigure(encoding="utf-8")

user = env["res.users"].browse(61)
emp = env["hr.employee"].browse(56)
lt = env["hr.leave.type"].browse(75)
print("type", lt.name, lt.leave_validation_type)

# create with sudo + skip validity
start = fields.Date.today() + timedelta(days=30)
with env.cr.savepoint():
    leave = env["hr.leave"].sudo().with_context(
        leave_fast_create=True,
        skip_handover_submit_bot_notify=True,
    ).create({
        "name": "diag",
        "employee_id": emp.id,
        "holiday_status_id": lt.id,
        "request_date_from": start,
        "request_date_to": start,
        "date_from": fields.Datetime.to_datetime(start),
        "date_to": fields.Datetime.to_datetime(start + timedelta(days=1)),
        "state": "confirm",
    })
    print("leave", leave.id, "state", leave.state)
    approvers = leave._get_multi_step_approvers()
    print("multi step approvers:", approvers.mapped("login"))
    print("khan in approvers:", user in approvers)
    print("can_multi_step_approve:", leave.with_user(user).can_multi_step_approve)
    try:
        leave.with_user(user).action_multi_step_approve()
        print("multi_step approve OK")
    except Exception as ex:
        print("multi_step approve FAIL:", ex)
    try:
        leave.with_user(user).action_approve()
        print("action_approve OK")
    except Exception as ex:
        print("action_approve FAIL:", ex)
