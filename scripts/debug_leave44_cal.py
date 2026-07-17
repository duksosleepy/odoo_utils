# -*- coding: utf-8 -*-
lv = env["hr.leave"].browse(44)
emp = lv.employee_id
print("leave resource_calendar_id", lv.resource_calendar_id.id)
print("employee version cal", emp.version_id.resource_calendar_id.id)
lv._compute_duration()
print("after compute days", lv.number_of_days, "hours", lv.number_of_hours)
