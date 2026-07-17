# -*- coding: utf-8 -*-
from datetime import datetime
import pytz

lv = env["hr.leave"].browse(44)
emp = lv.employee_id
print("leave from", lv.date_from, "to", lv.date_to)
print("request unit", lv.leave_type_request_unit)
print("employee cal", emp.version_id.resource_calendar_id.id)
print("attendance days", sorted(set(emp.version_id.resource_calendar_id.attendance_ids.mapped("dayofweek"))))

cal = emp.version_id.resource_calendar_id
tz = pytz.timezone(cal.tz or "UTC")
df = lv.date_from
dt = lv.date_to
work = emp._get_work_days_data_batch(df, dt, compute_leaves=True)
print("work batch", work)

list_wt = emp._list_work_time_per_day(df, dt)
print("list work time", list_wt)

durations = lv._get_durations()
print("durations", durations)
