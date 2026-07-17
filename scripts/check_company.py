# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
for eid in [8, 71, 81, 89]:
    e = env["hr.employee"].sudo().browse(eid)
    print(eid, e.name, "company", e.company_id.id, e.company_id.name)

print("anh company", u85.company_id.id, u85.company_ids.ids)
