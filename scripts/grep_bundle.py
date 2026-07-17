att = env["ir.attachment"].search([
    ("name", "=", "web.assets_web.min.js"),
    ("type", "=", "binary"),
], order="write_date desc", limit=1)
print("write_date", att.write_date, "size", att.file_size)
data = att.raw.decode("utf-8", errors="ignore")
for needle in ["hr_leave_analytics_dashboard", "LeaveAnalyticsDashboard", "hr_leave_analytics/static"]:
    print(needle, "->", needle in data)
