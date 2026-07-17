# -*- coding: utf-8 -*-
lv = env["hr.leave"].browse([43, 44])
print("cal ids", lv.mapped("resource_calendar_id.id"))
print("durations", lv._get_durations())
env.add_to_compute(lv._fields["number_of_days"], lv)
lv._recompute_recordset(["number_of_days", "number_of_hours"])
print("after recompute", [(l.id, l.number_of_days, l.number_of_hours) for l in lv])
env.cr.commit()
