# -*- coding: utf-8 -*-
Dashboard = env["hr.leave.analytics.dashboard"]
data = Dashboard.get_dashboard_data({"employee_mien": "VP", "year": 2026, "month": 6})
lines = [
    "is_vp_dashboard=%s" % data.get("is_vp_dashboard"),
    "location_column=%s" % data.get("location_column_label"),
    "top_title=%s" % data.get("top_location_title"),
    "kpi_total=%s pending=%s" % (data["kpi"].get("total_employees"), data["kpi"].get("pending_approval")),
    "top_groups=%s" % [(r.get("ma_bo_phan"), r.get("on_leave_count")) for r in data.get("top_stores", [])[:5]],
]
wf = data.get("leave_workflow_tables") or {}
for key in ("on_leave_today", "pending_approval", "pending_handover"):
    rows = wf.get(key) or []
    lines.append("%s: %s rows" % (key, len(rows)))
    for row in rows[:3]:
        lines.append("  %s | %s | %s" % (row.get("employee_name"), row.get("ma_bo_phan"), row.get("job_title")))
details = data.get("leave_details") or []
lines.append("details=%s non_vp=%s" % (
    len(details),
    [r.get("employee_name") for r in details if r.get("employee_mien") != "VP"],
))
print("\n".join(lines))
