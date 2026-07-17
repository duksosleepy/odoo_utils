# -*- coding: utf-8 -*-
env["hr.employee"].search([])._sync_store_working_calendar()
lv = env["hr.leave"].browse([43, 44])
for l in lv:
    print("before", l.id, l.number_of_days, l.resource_calendar_id.id)
env.cr.commit()
