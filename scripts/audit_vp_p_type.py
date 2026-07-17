# -*- coding: utf-8 -*-
import sys
from datetime import timedelta
from odoo import fields

sys.stdout.reconfigure(encoding="utf-8")

start = fields.Date.today() + timedelta(days=30)
dt_from = fields.Datetime.to_datetime(start)
dt_to = fields.Datetime.to_datetime(start + timedelta(days=1))
p_type = env["hr.leave.type"].sudo().browse(75)  # Nghỉ phép (P) for VP

vp_users = env["hr.employee"].sudo().search([
    ("active", "=", True), ("mien", "=", "VP"), ("user_id", "!=", False)
])

ok_list = []
fail_reasons = {}
for emp in vp_users:
    try:
        with env.cr.savepoint():
            env["hr.leave"].with_user(emp.user_id).with_context(
                skip_handover_submit_bot_notify=True,
                skip_responsible_submit_notify=True,
            ).create({
                "name": "audit", "employee_id": emp.id, "holiday_status_id": p_type.id,
                "request_date_from": start, "request_date_to": start,
                "date_from": dt_from, "date_to": dt_to,
            })
        ok_list.append(emp.user_id.login)
    except Exception as ex:
        key = str(ex).split("\n")[0][:90]
        fail_reasons.setdefault(key, []).append(emp.user_id.login)

print(f"VP users probe với loại '{p_type.name}' (id=75):")
print(f"  OK: {len(ok_list)}")
print(f"  FAIL: {sum(len(v) for v in fail_reasons.values())}")
for reason, logins in fail_reasons.items():
    print(f"\n  Lý do: {reason}")
    for lg in logins:
        print(f"    - {lg}")

# Bắc employee
bac = env["hr.employee"].sudo().browse(21)
print(f"\nNV Bắc id=21: {bac.name} user={bac.user_id.login if bac.user_id else 'KHÔNG CÓ USER'}")

# no_mien who succeeded
print("\nno_mien user tạo P1 OK:")
for emp in env["hr.employee"].sudo().search([("active", "=", True), ("mien", "=", False), ("user_id", "!=", False)]):
    try:
        with env.cr.savepoint():
            env["hr.leave"].with_user(emp.user_id).with_context(
                skip_handover_submit_bot_notify=True, skip_responsible_submit_notify=True,
            ).create({
                "name": "x", "employee_id": emp.id,
                "holiday_status_id": env["hr.leave.type"].search([("name", "ilike", "(P1)")], limit=1).id,
                "request_date_from": start, "request_date_to": start,
                "date_from": dt_from, "date_to": dt_to,
            })
        print(f"  OK: {emp.user_id.login} | {emp.name}")
    except Exception:
        pass
