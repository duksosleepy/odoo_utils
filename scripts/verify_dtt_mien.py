data = env["hr.leave.analytics.dashboard"].get_dashboard_data()
with open(r"d:\Lap_odoo\odoo_time_off_custom\scripts\verify_dtt_out.txt", "w", encoding="utf-8") as f:
    f.write("count=%s\n" % len(data["mien_comparison"]))
    for row in data["mien_comparison"]:
        f.write("%s|%s|%s\n" % (row["mien"], row["leave_days"], row["employee_count"]))
