data = env["hr.leave.analytics.dashboard"].with_context(dashboard_mien="Nam").get_dashboard_data({"employee_mien": "Nam"})
with open(r"d:\Lap_odoo\odoo_time_off_custom\scripts\verify_pie_out.txt", "w", encoding="utf-8") as f:
    f.write("mien_count=%s\n" % len(data["mien_comparison"]))
    for row in data["mien_comparison"]:
        f.write("%s=%s\n" % (row["mien"], row["leave_days"]))
    f.write("active_mien=%s\n" % data["active_mien"])
    f.write("employees=%s\n" % len(data["watch_employees"]))
