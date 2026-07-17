# -*- coding: utf-8 -*-
import sys
from datetime import timedelta
from odoo import fields

sys.stdout.reconfigure(encoding="utf-8")

start = fields.Date.today() + timedelta(days=30)
dt_from = fields.Datetime.to_datetime(start)
dt_to = fields.Datetime.to_datetime(start + timedelta(days=1))

samples = [
    ("VP blocked", "khan.nguyen@sangtam.com", 77),  # P2 wrong for VP
    ("VP blocked P", "khan.nguyen@sangtam.com", 75),  # P correct mien
    ("Nam OK", "nhi.cao@sangtam.com", 74),  # P1
    ("No mien store", "Cau.doan@sangtam.com", 74),
    ("Bắc", None, 74),  # emp 21
]

for label, login, type_id in samples:
    print(f"\n=== {label} ===")
    if login:
        user = env["res.users"].sudo().search([("login", "=", login)], limit=1)
        emp = user.employee_id
    else:
        emp = env["hr.employee"].sudo().browse(21)
        user = emp.user_id
    if not emp:
        print("  no employee")
        continue
    print(f"  {emp.name} mien={emp._get_leave_mien()!r}")
    Leave = env["hr.leave"].with_user(user) if user else env["hr.leave"]
    try:
        with env.cr.savepoint():
            lv = Leave.create({
                "name": "probe",
                "employee_id": emp.id,
                "holiday_status_id": type_id,
                "request_date_from": start,
                "request_date_to": start,
                "date_from": dt_from,
                "date_to": dt_to,
            })
            print(f"  CREATE OK id={lv.id} state={lv.state} type={lv.holiday_status_id.name}")
    except Exception as ex:
        print(f"  CREATE FAIL: {str(ex)[:150]}")

# Full matrix: per mien group, can any user create?
print("\n" + "=" * 60)
print("MA TRẬN: TẠO ĐƠN P1 CHO 1 USER MỖI NHÓM")
print("=" * 60)
groups = {
    "VP": env["hr.employee"].sudo().search([("active", "=", True), ("mien", "=", "VP")], limit=1),
    "Nam": env["hr.employee"].sudo().search([("active", "=", True), ("mien", "=", "Nam")], limit=1),
    "no_mien+user": env["hr.employee"].sudo().search([
        ("active", "=", True), ("mien", "=", False), ("user_id", "!=", False)
    ], limit=1),
}
p1 = env["hr.leave.type"].sudo().search([("name", "ilike", "(P1)")], limit=1)
for gname, emp in groups.items():
    if not emp:
        print(f"  {gname}: no employee")
        continue
    user = emp.user_id
    try:
        with env.cr.savepoint():
            lv = env["hr.leave"].with_user(user).create({
                "name": "probe", "employee_id": emp.id, "holiday_status_id": p1.id,
                "request_date_from": start, "request_date_to": start,
                "date_from": dt_from, "date_to": dt_to,
            })
            print(f"  {gname} ({emp.name}): OK")
    except Exception as ex:
        print(f"  {gname} ({emp.name}): FAIL — {str(ex)[:120]}")
