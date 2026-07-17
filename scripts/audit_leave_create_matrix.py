# -*- coding: utf-8 -*-
import sys
from datetime import timedelta
from odoo import fields

sys.stdout.reconfigure(encoding="utf-8")

start = fields.Date.today() + timedelta(days=30)
dt_from = fields.Datetime.to_datetime(start)
dt_to = fields.Datetime.to_datetime(start + timedelta(days=1))
p1 = env["hr.leave.type"].sudo().search([("name", "ilike", "(P1)")], limit=1)

Employee = env["hr.employee"].sudo()
active = Employee.search([("active", "=", True)])

results = {
    "VP": {"ok": 0, "fail": 0, "reasons": {}},
    "Nam": {"ok": 0, "fail": 0, "reasons": {}},
    "Bắc": {"ok": 0, "fail": 0, "reasons": {}},
    "ĐTT": {"ok": 0, "fail": 0, "reasons": {}},
    "no_mien": {"ok": 0, "fail": 0, "reasons": {}},
    "Tất cả": {"ok": 0, "fail": 0, "reasons": {}},
    "other": {"ok": 0, "fail": 0, "reasons": {}},
}

def bucket(emp):
    m = emp._get_leave_mien()
    if not m:
        return "no_mien"
    if m in results:
        return m
    return "other"

def short_err(ex):
    s = str(ex).split("\n")[0][:100]
    return s

for emp in active:
    if not emp.user_id or emp.user_id.share:
        continue
    b = bucket(emp)
    try:
        with env.cr.savepoint():
            env["hr.leave"].with_user(emp.user_id).with_context(
                skip_handover_submit_bot_notify=True,
                skip_responsible_submit_notify=True,
            ).create({
                "name": "audit_probe",
                "employee_id": emp.id,
                "holiday_status_id": p1.id,
                "request_date_from": start,
                "request_date_to": start,
                "date_from": dt_from,
                "date_to": dt_to,
            })
        results[b]["ok"] += 1
    except Exception as ex:
        results[b]["fail"] += 1
        key = short_err(ex)
        results[b]["reasons"][key] = results[b]["reasons"].get(key, 0) + 1

print("KẾT QUẢ TẠO ĐƠN P1 (user có login, 93 NV active)")
print("=" * 70)
for b in ("VP", "Nam", "Bắc", "ĐTT", "no_mien", "Tất cả", "other"):
    r = results[b]
    total = r["ok"] + r["fail"]
    if total == 0:
        print(f"\n[{b}] 0 user có login")
        continue
    print(f"\n[{b}] {total} user | OK={r['ok']} FAIL={r['fail']}")
    for reason, cnt in sorted(r["reasons"].items(), key=lambda x: -x[1]):
        print(f"    ({cnt}) {reason}")
