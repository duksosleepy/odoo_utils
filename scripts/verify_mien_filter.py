data_all = env["hr.leave.analytics.dashboard"].get_dashboard_data()
data_nam = env["hr.leave.analytics.dashboard"].with_context(dashboard_mien="Nam").get_dashboard_data(
    {"employee_mien": "Nam"}
)
with open(r"d:\Lap_odoo\odoo_time_off_custom\scripts\verify_mien_filter_out.txt", "w", encoding="utf-8") as f:
    f.write("ALL show_comparison=%s employees=%s\n" % (
        data_all["show_mien_comparison"],
        len(data_all["watch_employees"]),
    ))
    f.write("NAM show_comparison=%s employees=%s mien_rows=%s\n" % (
        data_nam["show_mien_comparison"],
        len(data_nam["watch_employees"]),
        len(data_nam["mien_comparison"]),
    ))
    for row in data_nam["watch_employees"]:
        f.write("emp %s job=%s\n" % (row["employee_name"], row.get("job_title")))
    for row in data_nam["top_stores"]:
        f.write("store %s job=%s\n" % (row["store_name"], row.get("job_title")))
