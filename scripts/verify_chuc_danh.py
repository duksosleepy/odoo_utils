rows = env["hr.leave.analytics.employee.watch"].search([], limit=5)
with open(r"d:\Lap_odoo\odoo_time_off_custom\scripts\verify_chuc_danh_out.txt", "w", encoding="utf-8") as f:
    for row in rows:
        emp = row.employee_id
        f.write("%s | key=%s | display=%s | emp.job_title=%s | version=%s\n" % (
            row.employee_name,
            row.job_title,
            row.job_title_display,
            emp.job_title if emp else "",
            emp.current_version_id.job_title if emp and emp.current_version_id else "",
        ))
