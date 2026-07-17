# -*- coding: utf-8 -*-
import sys
from collections import Counter, defaultdict
from datetime import timedelta
from odoo import fields

sys.stdout.reconfigure(encoding="utf-8")

Employee = env["hr.employee"].sudo()
MienConfig = env["hr.leave.mien.config"]
Leave = env["hr.leave"]
LeaveType = env["hr.leave.type"]
Allocation = env["hr.leave.allocation"]
start = fields.Date.today() + timedelta(days=30)

active = Employee.search([("active", "=", True)])

# 1) Employees without leave mien - breakdown
print("=" * 72)
print("69 NV KHÔNG CÓ MIỀN NGHỈ PHÉP — PHÂN TÍCH")
print("=" * 72)
no_mien = []
for emp in active:
    if not emp._get_leave_mien():
        no_mien.append(emp)

ma_bo_phan_mien = Counter()
has_user = 0
for emp in no_mien:
    mbp = emp.ma_bo_phan_id.mien if emp.ma_bo_phan_id else None
    ma_bo_phan_mien[mbp or "(trống)"] += 1
    if emp.user_id:
        has_user += 1

print(f"Tổng: {len(no_mien)} | Có user login: {has_user}")
print("Miền mã bộ phận (ma_bo_phan_id.mien):")
for k, v in ma_bo_phan_mien.most_common():
    print(f"  {k}: {v} NV")

# sample with user + ma_bo_phan mien
print("\nMẫu NV có user nhưng không có leave mien (field mien trống):")
count = 0
for emp in no_mien:
    if not emp.user_id:
        continue
    mbp = emp.ma_bo_phan_id.mien if emp.ma_bo_phan_id else None
    if mbp:
        print(f"  id={emp.id} {emp.name} | login={emp.user_id.login} | ma_bo_phan.mien={mbp} | emp.mien={emp.mien or '(trống)'}")
        count += 1
        if count >= 20:
            break

# 2) If we infer mien from ma_bo_phan, how many per region?
print("\n" + "=" * 72)
print("PHÂN BỐ NẾU LẤY MIỀN TỪ ma_bo_phan_id (khi emp.mien trống)")
print("=" * 72)
inferred = Counter()
for emp in active:
    m = emp.mien or (emp.ma_bo_phan_id.mien if emp.ma_bo_phan_id else False)
    inferred[m or "(trống)"] += 1
for k, v in inferred.most_common():
    print(f"  {k}: {v} NV")

# 3) Nam employees detail
print("\n" + "=" * 72)
print("CHI TIẾT 6 NV MIỀN NAM")
print("=" * 72)
nam_emps = [e for e in active if e._get_leave_mien() == "Nam"]
for emp in nam_emps:
    allowed = LeaveType.with_context(employee_id=emp.id).search(
        Leave._leave_type_domain_for_employee(emp, start_date=start, end_date=start)
    )
    print(f"  id={emp.id} {emp.name} | {emp.user_id.login if emp.user_id else 'no user'} | types={allowed.mapped('name')}")

# 4) VP - any allocation in system?
print("\n" + "=" * 72)
print("ALLOCATION TRONG HỆ THỐNG (validate)")
print("=" * 72)
vp_type_ids = MienConfig._get_leave_type_ids_for_mien("VP")
all_allocs = Allocation.search([("state", "=", "validate")])
print(f"Tổng allocation validate: {len(all_allocs)}")
by_type = Counter()
for a in all_allocs:
    by_type[a.holiday_status_id.name] += 1
for name, cnt in by_type.most_common(15):
    print(f"  {name}: {cnt}")
vp_allocs = all_allocs.filtered(lambda a: a.holiday_status_id.id in vp_type_ids)
print(f"Allocation cho loại VP: {len(vp_allocs)}")
if vp_allocs:
    for a in vp_allocs[:10]:
        print(f"  emp={a.employee_id.name} type={a.holiday_status_id.name} days={a.number_of_days}")

# 5) Mien config records in DB
print("\n" + "=" * 72)
print("BẢN GHI hr.leave.mien.config")
print("=" * 72)
for cfg in MienConfig.search([]):
    print(f"  mien={cfg.mien} lines={len(cfg.line_ids)} types={cfg.line_ids.leave_type_id.mapped('name')}")

# 6) Employees with emp.mien field set directly
print("\n" + "=" * 72)
print("NV CÓ FIELD emp.mien ĐƯỢC SET")
print("=" * 72)
direct = Counter()
for emp in active:
    if emp.mien:
        direct[emp.mien] += 1
for k, v in direct.most_common():
    print(f"  {k}: {v} NV")

# 7) Users with login in no-mien group who would work if mien inferred
print("\n" + "=" * 72)
print("USER LOGIN TRONG NHÓM 'KHÔNG MIỀN' — NẾU SỬA MIỀN TỪ ma_bo_phan")
print("=" * 72)
would_ok = defaultdict(list)
would_fail = defaultdict(list)
for emp in no_mien:
    if not emp.user_id or emp.user_id.share:
        continue
    inferred_mien = emp.ma_bo_phan_id.mien if emp.ma_bo_phan_id else False
    if not inferred_mien:
        would_fail["no_ma_bo_phan"].append(emp)
        continue
    if not MienConfig._is_mien_configured(inferred_mien):
        would_fail[f"mien_{inferred_mien}_not_configured"].append(emp)
        continue
    # simulate with inferred mien - hack by temporarily checking types for that mien
    type_ids = MienConfig._get_leave_type_ids_for_mien(inferred_mien)
    types = LeaveType.browse(type_ids)
    if all(t.requires_allocation for t in types):
        allocs = Allocation.search([("employee_id", "=", emp.id), ("state", "=", "validate")], limit=1)
        if not allocs:
            would_fail[f"mien_{inferred_mien}_need_alloc"].append(emp)
        else:
            would_ok[inferred_mien].append(emp)
    else:
        would_ok[inferred_mien].append(emp)

for mien, emps in sorted(would_ok.items()):
    print(f"\n  [{mien}] sẽ OK ({len(emps)} user):")
    for e in emps[:10]:
        print(f"    {e.user_id.login} | {e.name}")
    if len(emps) > 10:
        print(f"    ... +{len(emps)-10}")

for reason, emps in sorted(would_fail.items()):
    print(f"\n  [{reason}] vẫn lỗi ({len(emps)} user):")
    for e in emps[:8]:
        print(f"    {e.user_id.login} | {e.name}")
    if len(emps) > 8:
        print(f"    ... +{len(emps)-8}")
