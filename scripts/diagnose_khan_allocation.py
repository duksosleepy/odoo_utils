# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

emp = env["hr.employee"].browse(56)
print("employee:", emp.name)
for f in ("tong_so_phep", "so_phep_con_lai", "so_phep_da_su_dung"):
    if hasattr(emp, f):
        print(f, ":", getattr(emp, f))

allocs = env["hr.leave.allocation"].sudo().search([("employee_id", "=", 56)])
print("allocations:", len(allocs))
for a in allocs:
    print(f"  alloc {a.id} type={a.holiday_status_id.name!r} state={a.state} days={a.number_of_days} remaining={a.max_leaves - a.leaves_taken if hasattr(a, 'max_leaves') else '?'}")

# allowed VP types
MienConfig = env["hr.leave.mien.config"]
allowed = MienConfig._get_leave_type_ids_for_mien("VP")
print("\nVP allowed types:")
for tid in allowed:
    t = env["hr.leave.type"].browse(tid)
    print(f"  {tid} {t.name!r} requires_allocation={t.requires_allocation}")

# check domain from onchange
Leave = env["hr.leave"].with_user(env["res.users"].browse(61))
leave = Leave.new({"employee_id": emp.id})
if hasattr(leave, "_search_allowed_leave_types"):
    from datetime import date, timedelta
    start = date.today() + timedelta(days=30)
    allowed_recs = leave._search_allowed_leave_types(emp, start_date=start, end_date=start)
    print("\nonchange allowed types:", allowed_recs.mapped("name"))
