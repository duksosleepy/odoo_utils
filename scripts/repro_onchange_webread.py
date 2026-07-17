# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u = env["res.users"].browse(85)
Emp = env["hr.employee"].with_user(u)
e = Emp.browse(88)

cases = [
    {},
    {"id": {}},
    {"name": {}},
    {"work_phone": {}},
]
for spec in cases:
    try:
        r = e.web_read(spec)
        print("spec", spec or "empty", "->", len(r), "rows", r[:1])
    except Exception as ex:
        print("spec", spec, "FAIL", ex)

# Simulate onchange diff with empty simple_fields_spec
r = e.web_read({})
print("onchange empty spec rows", len(r))
