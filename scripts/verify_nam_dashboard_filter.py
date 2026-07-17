# -*- coding: utf-8 -*-
"""Verify Dashboard Miền Nam only returns Nam-region employees."""
Dashboard = env["hr.leave.analytics.dashboard"]
data = Dashboard.get_dashboard_data({"employee_mien": "Nam", "year": 2026, "month": 6})
wf = data.get("leave_workflow_tables") or {}
pending = wf.get("pending_approval") or []
details = data.get("leave_details") or []

lines = [
    "=== Pending approval (Nam dashboard) ===",
]
for row in pending:
    lines.append(
        "%s | store=%s | job=%s | days=%s"
        % (row.get("employee_name"), row.get("store_name"), row.get("job_title"), row.get("number_of_days"))
    )

lines.append("\n=== Detail table sample (first 15) ===")
for row in details[:15]:
    lines.append(
        "%s | mien=%s | store=%s"
        % (row.get("employee_name"), row.get("employee_mien"), row.get("ma_bo_phan"))
    )

bad_pending = [r for r in pending if r.get("employee_name") and "VP" in (r.get("job_title") or "")]
bad_details = [r for r in details if r.get("employee_mien") and r.get("employee_mien") != "Nam"]
lines.append("\nVP in pending: %s" % [r.get("employee_name") for r in bad_pending])
lines.append("Non-Nam in details: %s" % len(bad_details))

out = "\n".join(lines)
print(out)
with open(r"d:\Lap_odoo\odoo_time_off_custom\scripts\verify_nam_dashboard_filter_out.txt", "w", encoding="utf-8") as f:
    f.write(out)
