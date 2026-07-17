all_data = env["hr.leave.analytics.dashboard"].get_dashboard_data()
nam_data = env["hr.leave.analytics.dashboard"].get_dashboard_data({"employee_mien": "Nam"})
with open(r"d:\Lap_odoo\odoo_time_off_custom\scripts\verify_regional_out.txt", "w", encoding="utf-8") as f:
    f.write("TONG QUAN miens=%s regional=%s\n" % (
        [r["mien"] for r in all_data["mien_comparison"]],
        all_data["is_regional_dashboard"],
    ))
    f.write("NAM miens=%s regional=%s title=%s\n" % (
        [r["mien"] for r in nam_data["mien_comparison"]],
        nam_data["is_regional_dashboard"],
        nam_data["mien_chart_title"],
    ))
