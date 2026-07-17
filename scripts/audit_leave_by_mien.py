# -*- coding: utf-8 -*-
"""Audit leave-submit readiness for all employees by Miền (Bắc, Nam, ĐTT, VP).

Run:
  Get-Content -Encoding UTF8 scripts/audit_leave_by_mien.py | python odoo\\odoo-bin shell -c odoo.conf -d lap_odoo19 --no-http
"""
import sys
from collections import defaultdict
from datetime import timedelta

from odoo import fields

sys.stdout.reconfigure(encoding="utf-8")

MIENS = ("Bắc", "Nam", "ĐTT", "VP")
Employee = env["hr.employee"].sudo()
MienConfig = env["hr.leave.mien.config"]
Leave = env["hr.leave"]
LeaveType = env["hr.leave.type"]
Allocation = env["hr.leave.allocation"]

start = fields.Date.today() + timedelta(days=30)

# --- mien config summary ---
print("=" * 72)
print("CẤU HÌNH MIỀN (hr.leave.mien.config)")
print("=" * 72)
mien_type_info = {}
for mien in MIENS:
    type_ids = MienConfig._get_leave_type_ids_for_mien(mien)
    types = LeaveType.browse(type_ids)
    no_alloc = types.filtered(lambda t: not t.requires_allocation)
    need_alloc = types.filtered(lambda t: t.requires_allocation)
    mien_type_info[mien] = {
        "configured": MienConfig._is_mien_configured(mien),
        "type_ids": type_ids,
        "no_alloc_names": no_alloc.mapped("name"),
        "need_alloc_names": need_alloc.mapped("name"),
    }
    print(f"\n[{mien}] configured={mien_type_info[mien]['configured']} types={len(type_ids)}")
    if no_alloc:
        print(f"  Không cần allocation ({len(no_alloc)}): {', '.join(no_alloc.mapped('name')[:8])}")
        if len(no_alloc) > 8:
            print(f"    ... +{len(no_alloc) - 8} loại khác")
    if need_alloc:
        print(f"  Cần allocation ({len(need_alloc)}): {', '.join(need_alloc.mapped('name')[:8])}")
        if len(need_alloc) > 8:
            print(f"    ... +{len(need_alloc) - 8} loại khác")

# --- employees ---
active = Employee.search([("active", "=", True)])
print("\n" + "=" * 72)
print(f"NHÂN VIÊN ĐANG HOẠT ĐỘNG: {len(active)}")
print("=" * 72)

by_mien = defaultdict(list)
no_mien = []
for emp in active:
    mien = emp._get_leave_mien() if hasattr(emp, "_get_leave_mien") else False
    if not mien:
        no_mien.append(emp)
        continue
    by_mien[mien].append(emp)

for m in MIENS:
    print(f"  {m}: {len(by_mien.get(m, []))} NV")
print(f"  (không xác định miền): {len(no_mien)} NV")

# pre-fetch allocations by employee
alloc_by_emp = defaultdict(list)
for alloc in Allocation.search([("employee_id", "in", active.ids), ("state", "=", "validate")]):
    alloc_by_emp[alloc.employee_id.id].append(alloc)

issues = defaultdict(list)  # issue_code -> list of (emp, detail)


def allowed_types_for_employee(emp):
    """Types matching mien + allocation domain (same as form onchange)."""
    domain = Leave._leave_type_domain_for_employee(
        emp, start_date=start, end_date=start
    )
    return LeaveType.with_context(employee_id=emp.id).search(domain)


def classify_employee(emp, mien):
    user = emp.user_id
    login = user.login if user else None
    tong = getattr(emp, "tong_so_phep", None)
    allocs = alloc_by_emp.get(emp.id, [])
    allowed = allowed_types_for_employee(emp)
    config_ids = set(MienConfig._get_leave_type_ids_for_mien(mien) or [])

    detail = {
        "id": emp.id,
        "name": emp.name,
        "login": login or "(không có user)",
        "mien": mien,
        "dept": emp.department_id.name or "",
        "job": getattr(emp, "job_title", "") or "",
        "tong_so_phep": tong,
        "alloc_count": len(allocs),
        "allowed_count": len(allowed),
        "allowed_names": allowed.mapped("name"),
    }

    if not MienConfig._is_mien_configured(mien):
        issues["mien_not_configured"].append((emp, detail))
        return "mien_not_configured", detail

    if not config_ids:
        issues["mien_empty_types"].append((emp, detail))
        return "mien_empty_types", detail

    if not allowed:
        # why empty?
        config_types = LeaveType.browse(list(config_ids))
        only_need_alloc = all(t.requires_allocation for t in config_types)
        if only_need_alloc and not allocs:
            issues["no_allocation_vp_style"].append((emp, detail))
            return "no_allocation_vp_style", detail
        if only_need_alloc and allocs:
            issues["allocation_not_valid"].append((emp, detail))
            return "allocation_not_valid", detail
        issues["no_allowed_types_other"].append((emp, detail))
        return "no_allowed_types_other", detail

    if not user:
        issues["no_user_but_ok_types"].append((emp, detail))
        return "no_user_but_ok_types", detail

    return "ok", detail


# audit each mien
summary = {}
for mien in list(MIENS) + ["(không miền)"]:
    summary[mien] = defaultdict(int)

print("\n" + "=" * 72)
print("KẾT QUẢ RÀ SOÁT THEO MIỀN")
print("=" * 72)

for mien in MIENS:
    emps = by_mien.get(mien, [])
    print(f"\n### MIỀN {mien} — {len(emps)} nhân viên ###")
    counts = defaultdict(int)
    blocked_samples = []
    for emp in emps:
        status, detail = classify_employee(emp, mien)
        counts[status] += 1
        summary[mien][status] += 1
        if status != "ok" and len(blocked_samples) < 15:
            blocked_samples.append((status, detail))

    print(f"  OK (có loại nghỉ hợp lệ): {counts['ok']}")
    print(f"  Không có loại nghỉ hợp lệ (cần allocation): {counts['no_allocation_vp_style']}")
    print(f"  Allocation có nhưng không khớp domain: {counts['allocation_not_valid']}")
    print(f"  Không có loại (lý do khác): {counts['no_allowed_types_other']}")
    print(f"  Có loại OK nhưng không có user đăng nhập: {counts['no_user_but_ok_types']}")

    if blocked_samples:
        print(f"  --- Mẫu NV bị chặn (tối đa 15) ---")
        for status, d in blocked_samples:
            print(
                f"    [{status}] id={d['id']} {d['name']} | {d['login']} | "
                f"alloc={d['alloc_count']} tong_phep={d['tong_so_phep']} | {d['dept']}"
            )

# no mien employees
if no_mien:
    print(f"\n### KHÔNG XÁC ĐỊNH MIỀN — {len(no_mien)} nhân viên ###")
    for emp in no_mien[:20]:
        issues["no_mien"].append((emp, {"id": emp.id, "name": emp.name, "login": emp.user_id.login if emp.user_id else None}))
        summary["(không miền)"]["no_mien"] += 1
        print(
            f"    id={emp.id} {emp.name} | mien_field={getattr(emp, 'mien', None)} | "
            f"ma_bo_phan_mien={emp.ma_bo_phan_id.mien if emp.ma_bo_phan_id else None}"
        )
    if len(no_mien) > 20:
        print(f"    ... +{len(no_mien) - 20} NV khác")

# spot-check: users with login who cannot submit
print("\n" + "=" * 72)
print("USER CÓ LOGIN NHƯNG KHÔNG CÓ LOẠI NGHỈ HỢP LỆ (toàn hệ thống)")
print("=" * 72)
blocked_users = []
for mien in MIENS:
    for emp in by_mien.get(mien, []):
        if not emp.user_id or emp.user_id.share:
            continue
        status, detail = classify_employee(emp, mien)
        if status != "ok":
            blocked_users.append((mien, status, detail))

print(f"Tổng: {len(blocked_users)} user")
for mien in MIENS:
    subset = [x for x in blocked_users if x[0] == mien]
    if not subset:
        print(f"\n[{mien}] Tất cả user có login đều có ít nhất 1 loại nghỉ hợp lệ.")
        continue
    print(f"\n[{mien}] {len(subset)} user bị chặn:")
    for _, status, d in subset[:30]:
        print(f"  {d['login']} | {d['name']} | {status} | alloc={d['alloc_count']} | tong={d['tong_so_phep']}")
    if len(subset) > 30:
        print(f"  ... +{len(subset) - 30} user khác")

# compare khan.nguyen
print("\n" + "=" * 72)
print("KIỂM TRA LẠI khan.nguyen")
print("=" * 72)
khan = env["res.users"].sudo().search([("login", "=", "khan.nguyen@sangtam.com")], limit=1)
if khan and khan.employee_id:
    st, det = classify_employee(khan.employee_id, khan.employee_id._get_leave_mien())
    print(f"  status={st}")
    print(f"  allowed_types={det['allowed_names']}")
    print(f"  alloc_count={det['alloc_count']} tong_so_phep={det['tong_so_phep']}")

# grand totals
print("\n" + "=" * 72)
print("TỔNG HỢP")
print("=" * 72)
total_ok = sum(summary[m].get("ok", 0) for m in MIENS)
total_blocked_alloc = sum(summary[m].get("no_allocation_vp_style", 0) for m in MIENS)
total_no_mien = len(no_mien)
total_with_user_blocked = len(blocked_users)
print(f"  NV active có miền: {sum(len(by_mien.get(m, [])) for m in MIENS)}")
print(f"  NV OK (có loại nghỉ): {total_ok}")
print(f"  NV thiếu allocation (miền chỉ có loại cần alloc): {total_blocked_alloc}")
print(f"  NV không xác định miền: {total_no_mien}")
print(f"  User login bị chặn gửi đơn: {total_with_user_blocked}")
