# -*- coding: utf-8 -*-
import sys
from datetime import timedelta
from odoo import fields

sys.stdout.reconfigure(encoding="utf-8")

Employee = env["hr.employee"].sudo()
Leave = env["hr.leave"]
LeaveType = env["hr.leave.type"]
MienConfig = env["hr.leave.mien.config"]
start = fields.Date.today() + timedelta(days=30)

# edge cases: mien not in standard list
print("NV có emp.mien ngoài Bắc/Nam/ĐTT/VP:")
for emp in Employee.search([("active", "=", True), ("mien", "!=", False)]):
    if emp.mien not in ("Bắc", "Nam", "ĐTT", "VP"):
        allowed = LeaveType.with_context(employee_id=emp.id).search(
            Leave._leave_type_domain_for_employee(emp, start_date=start, end_date=start)
        )
        print(f"  id={emp.id} mien={emp.mien!r} {emp.name} types={allowed.mapped('name')}")

print("\nNV Miền Bắc:")
for emp in Employee.search([("active", "=", True), ("mien", "=", "Bắc")]):
    allowed = LeaveType.with_context(employee_id=emp.id).search(
        Leave._leave_type_domain_for_employee(emp, start_date=start, end_date=start)
    )
    print(f"  id={emp.id} {emp.name} login={emp.user_id.login if emp.user_id else None} types={allowed.mapped('name')}")

print("\nNV Miền ĐTT:")
for emp in Employee.search([("active", "=", True), ("mien", "=", "ĐTT")]):
    allowed = LeaveType.with_context(employee_id=emp.id).search(
        Leave._leave_type_domain_for_employee(emp, start_date=start, end_date=start)
    )
    print(f"  id={emp.id} {emp.name} types={allowed.mapped('name')}")
if not Employee.search([("active", "=", True), ("mien", "=", "ĐTT")]):
    print("  (không có)")

# no mien sample - what domain returns?
print("\nMẫu 5 NV không miền — loại nghỉ hợp lệ:")
no_mien = Employee.search([("active", "=", True), ("mien", "=", False)])
count = 0
for emp in no_mien:
    if emp._get_leave_mien():
        continue
    allowed = LeaveType.with_context(employee_id=emp.id).search(
        Leave._leave_type_domain_for_employee(emp, start_date=start, end_date=start)
    )
    if emp.user_id:
        print(f"  id={emp.id} {emp.name} | {emp.user_id.login} | allowed={len(allowed)} {allowed.mapped('name')[:3]}")
        count += 1
        if count >= 5:
            break

# store-linked mien?
print("\nKiểm tra field mien/store trên NV cửa hàng (mẫu):")
for emp in no_mien.filtered(lambda e: e.user_id)[:5]:
    extras = []
    for f in ("store_id", "employee_mien", "mien_zone_id"):
        if hasattr(emp, f):
            val = getattr(emp, f)
            extras.append(f"{f}={val.display_name if hasattr(val, 'display_name') else val}")
    print(f"  {emp.name}: {', '.join(extras) or 'no extra fields'}")
