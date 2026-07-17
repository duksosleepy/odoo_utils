# -*- coding: utf-8 -*-
emps = env["hr.employee"].sudo().search([("mien", "=", "VP")])
for e in emps:
    print(e.id, e.name.encode("unicode_escape").decode())
