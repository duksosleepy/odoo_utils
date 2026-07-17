# -*- coding: utf-8 -*-
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

mod = env["ir.module.module"].search([("name", "=", "hr_public_holiday_mien")], limit=1)
print("=== MODULE ===")
print(f"hr_public_holiday_mien state={mod.state} version={mod.latest_version}")

Employee = env["hr.employee"]
Leaves = env["resource.calendar.leaves"]
start = datetime(2026, 1, 1)
end = datetime(2026, 12, 31, 23, 59, 59)

all_h = Leaves.sudo().search([("resource_id", "=", False)])
print(f"\n=== ALL PUBLIC HOLIDAYS (global) count={len(all_h)} ===")
for h in all_h[:20]:
    scope = getattr(h, "holiday_scope", "n/a")
    print(f"  id={h.id} scope={scope} {h.date_from.date()}..{h.date_to.date()} | {h.name}")

h2026 = Leaves.sudo().search([
    ("resource_id", "=", False),
    ("date_from", "<=", end),
    ("date_to", ">=", start),
])
print(f"\n=== PUBLIC HOLIDAYS in 2026 count={len(h2026)} ===")

targets = Employee.search([
    "|", "|",
    ("name", "ilike", "Cao Ngoc Nhi"),
    ("name", "ilike", "Cao Ngọc Nhi"),
    ("mien", "in", ["Nam", "Bắc", "ĐTT", "VP"]),
], limit=8)
print(f"\n=== EMPLOYEE HOLIDAY RESOLUTION ===")
for e in targets:
    mien = e._employee_schedule_mien() if hasattr(e, "_employee_schedule_mien") else e.mien
    ph = e._get_public_holidays(start, end)
    ctx_emp = env["hr.employee"].with_context(employee_id=e.id)
    data = ctx_emp.get_special_days_data("2026-01-01 00:00:00", "2026-12-31 23:59:59")
    bank = data.get("bankHolidays", [])
    print(f"  {e.name} | mien={mien!r} | _get_public_holidays={len(ph)} | bankHolidays={len(bank)}")
    if bank:
        print(f"    first: {bank[0].get('title')}")

# Simulate logged-in store user search filter (old bug path)
print("\n=== resource.calendar.leaves search AS store user ===")
store_emp = Employee.search([("mien", "=", "Nam")], limit=1)
if store_emp:
    user = store_emp.user_id
    if user:
        as_user = env["resource.calendar.leaves"].with_user(user)
        scoped = as_user.search([
            ("resource_id", "=", False),
            ("date_from", "<=", end),
            ("date_to", ">=", start),
        ])
        skip = as_user.with_context(hr_public_holiday_mien_skip_scope_search=True).search([
            ("resource_id", "=", False),
            ("date_from", "<=", end),
            ("date_to", ">=", start),
        ])
        print(f"  user={user.login} scoped_search={len(scoped)} skip_ctx_search={len(skip)}")
