# -*- coding: utf-8 -*-
"""Cấp allocation Nghỉ phép (P) hàng loạt cho NV Miền VP.

Chạy (dry-run — chỉ in, không ghi DB):
  Get-Content -Encoding UTF8 scripts/grant_vp_leave_allocation.py | python odoo\\odoo-bin shell -c odoo.conf -d lap_odoo19 --no-http

Chạy thật: sửa DRY_RUN = False rồi chạy lại.

Yêu cầu: user shell phải có quyền HR Officer (admin OK).
"""
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

# --- cấu hình ---
DRY_RUN = False
LEAVE_TYPE_ID = 75  # Nghỉ phép (P)
DAYS = 12.0  # số ngày phép cấp (chỉnh theo quy định công ty)
DATE_FROM = date(2026, 1, 1)
DATE_TO = date(2026, 12, 31)
ONLY_LOGINS = []  # ví dụ ["khan.nguyen@sangtam.com"] — để [] = tất cả VP

LeaveType = env["hr.leave.type"].sudo().browse(LEAVE_TYPE_ID)
if not LeaveType.exists():
    raise SystemExit(f"Không tìm thấy loại nghỉ id={LEAVE_TYPE_ID}")

employees = env["hr.employee"].sudo().search([
    ("active", "=", True),
    ("mien", "=", "VP"),
])
if ONLY_LOGINS:
    employees = employees.filtered(lambda e: e.user_id.login in ONLY_LOGINS)

Allocation = env["hr.leave.allocation"].sudo()
created = skipped = 0

print(f"Loại: {LeaveType.name} (id={LEAVE_TYPE_ID})")
print(f"Số ngày: {DAYS} | Từ {DATE_FROM} đến {DATE_TO}")
print(f"DRY_RUN={DRY_RUN} | NV VP: {len(employees)}")
print("-" * 60)

for emp in employees:
    existing = Allocation.search([
        ("employee_id", "=", emp.id),
        ("holiday_status_id", "=", LEAVE_TYPE_ID),
        ("state", "=", "validate"),
    ], limit=1)
    login = emp.user_id.login if emp.user_id else "(no user)"
    if existing:
        print(f"SKIP {emp.name} | {login} — đã có allocation validate id={existing.id}")
        skipped += 1
        continue

    vals = {
        "name": f"{LeaveType.name} {DATE_FROM.year}",
        "holiday_status_id": LEAVE_TYPE_ID,
        "employee_id": emp.id,
        "number_of_days": DAYS,
        "date_from": DATE_FROM,
        "date_to": DATE_TO,
        "allocation_type": "regular",
    }
    print(f"CREATE {emp.name} | {login} | {DAYS} ngày")
    if DRY_RUN:
        created += 1
        continue

    alloc = Allocation.with_context(
        mail_notify_force_send=False,
        mail_activity_automation_skip=True,
    ).create(vals)
    # Duyệt allocation (giống wizard Odoo)
    if alloc.validation_type in ("no_validation", "hr") or env.user.has_group("hr_holidays.group_hr_holidays_user"):
        alloc.action_approve()
    if alloc.state != "validate" and alloc.can_approve:
        alloc.action_approve()
    print(f"  -> allocation id={alloc.id} state={alloc.state}")
    created += 1

if not DRY_RUN:
    env.cr.commit()
    print("Đã commit vào database.")

print("-" * 60)
print(f"{'Sẽ tạo' if DRY_RUN else 'Đã tạo'}: {created} | Bỏ qua (đã có): {skipped}")
if DRY_RUN:
    print("Để ghi DB: mở scripts/grant_vp_leave_allocation.py, đặt DRY_RUN = False, chạy lại.")
