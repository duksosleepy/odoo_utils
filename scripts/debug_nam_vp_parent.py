# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
for e in env["hr.employee"].sudo().search([("mien", "=", "Nam")]):
    p = e.parent_id
    if p and p.mien and p.mien not in ("Nam", "ĐTT", "Bắc", "Tất cả", False):
        print(e.id, e.name, "parent", p.id, p.name, "parent_mien", p.mien)
