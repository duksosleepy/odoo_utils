# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
for eid in [8, 71]:
    e = env["hr.employee"].sudo().browse(eid)
    p = env["hr.employee.public"].sudo().browse(eid)
    print(eid, "emp.mien", e.mien, "pub.mien", p.mien)
