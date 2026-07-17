# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
for m in ["Nam", "ĐTT", "Bắc", "VP"]:
    c = env["hr.employee"].sudo().search_count([("mien", "=", m)])
    v = env["hr.employee.public"].with_user(env["res.users"].browse(58)).search_count([("mien", "=", m)])
    print(m, "total", c, "visible", v)
