# -*- coding: utf-8 -*-
Dashboard = env["hr.leave.analytics.dashboard"]
opts = Dashboard.get_filter_options({"employee_mien": "Nam", "year": 2026, "month": 6})
codes = opts.get("ma_bo_phans") or []
lug_kdv = next((c for c in codes if c["name"] == "LUG_KDV"), None)
lines = ["ma_bo_phans count=%s" % len(codes), "sample=%s" % codes[:5]]
if lug_kdv:
    data = Dashboard.get_dashboard_data({
        "employee_mien": "Nam", "year": 2026, "month": 6,
        "ma_bo_phan_id": lug_kdv["id"],
    })
    details = data.get("leave_details") or []
    lines.append("filter LUG_KDV details=%s names=%s" % (
        len(details), [r.get("ma_bo_phan") for r in details[:5]]))
    bad = [r for r in details if r.get("ma_bo_phan") != "LUG_KDV"]
    lines.append("bad rows=%s" % len(bad))
print("\n".join(lines))
