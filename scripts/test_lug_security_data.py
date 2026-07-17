Session = env["lug.user.session"].sudo()
print("sessions:", Session.search_count([]))
print("with job title:", Session.search_count([("job_title_label", "!=", False)]))
for s in Session.search([], limit=3):
    print(s.user_id.name, s.job_title_label, s.mien_label)
Daily = env["lug.user.daily.summary"].sudo()
print("daily rows:", Daily.search_count([]))
for d in Daily.search([], limit=3):
    print(d.summary_date, d.user_id.name, d.job_title_label, d.total_hours_display)
