# -*- coding: utf-8 -*-
import sys
from datetime import timedelta
from odoo import fields
sys.stdout.reconfigure(encoding="utf-8")
user = env["res.users"].sudo().search([("login", "=", "theanh.khong@sangtam.com")], limit=1)
emp = user.employee_id
print("mien repr:", repr(emp._get_leave_mien()))
start = fields.Date.today() + timedelta(days=30)
p1 = env["hr.leave.type"].search([("name", "ilike", "(P1)")], limit=1)
try:
    with env.cr.savepoint():
        lv = env["hr.leave"].with_user(user).create({
            "name": "t", "employee_id": emp.id, "holiday_status_id": p1.id,
            "request_date_from": start, "request_date_to": start,
            "date_from": fields.Datetime.to_datetime(start),
            "date_to": fields.Datetime.to_datetime(start + timedelta(days=1)),
        })
    print("P1 OK", lv.holiday_status_id.name)
except Exception as ex:
    print("P1 FAIL:", str(ex)[:150])
