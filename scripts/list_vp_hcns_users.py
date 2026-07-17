# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

emps = env["hr.employee"].sudo().search([
    ("mien", "=", "VP"),
    ("user_id", "!=", False),
], order="job_title, name")
print("VP employees with login:")
for e in emps:
    print(f"  {e.name} title={e.job_title!r} login={e.user_id.login}")

hcns = env["hr.employee"].sudo().search([
    ("department_id.name", "ilike", "HÀNH CHÍNH"),
    ("user_id", "!=", False),
])
print("\nHCNS with login:")
for e in hcns:
    print(f"  {e.name} title={e.job_title!r} login={e.user_id.login}")
