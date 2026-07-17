# -*- coding: utf-8 -*-
import sys
from datetime import timedelta
from odoo import fields

sys.stdout.reconfigure(encoding="utf-8")

login = "khan.nguyen@sangtam.com"
user = env["res.users"].sudo().search([("login", "=", login)], limit=1)
emp = user.employee_id
print("employee", emp.id, emp.name)
mien = emp._get_leave_mien() if hasattr(emp, "_get_leave_mien") else None
print("leave mien:", mien)
MienConfig = env["hr.leave.mien.config"]
if mien:
    print("mien configured:", MienConfig._is_mien_configured(mien))
    allowed = MienConfig._get_leave_type_ids_for_mien(mien)
    print("allowed type ids:", allowed)
    for tid in allowed:
        t = env["hr.leave.type"].browse(tid)
        print(f"  {tid} {t.name!r} validation={t.leave_validation_type}")

Leave = env["hr.leave"].with_user(user)
types = env["hr.leave.type"].with_user(user).search([])
print("\nprobe all visible types:")
for t in types:
    start = fields.Date.today() + timedelta(days=30)
    try:
        with env.cr.savepoint():
            Leave.create({
                "name": "probe",
                "employee_id": emp.id,
                "holiday_status_id": t.id,
                "request_date_from": start,
                "request_date_to": start,
                "date_from": fields.Datetime.to_datetime(start),
                "date_to": fields.Datetime.to_datetime(start + timedelta(days=1)),
            })
        print(f"  OK {t.id} {t.name!r} val={t.leave_validation_type}")
    except Exception as ex:
        print(f"  FAIL {t.id} {t.name!r}: {str(ex)[:120]}")
