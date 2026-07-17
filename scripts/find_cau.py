# -*- coding: utf-8 -*-
emps = env["hr.employee"].sudo().search([])
for e in emps:
    n = e.name or ""
    if "C" in n or "Do" in n:
        pass
for e in env["hr.employee"].sudo().search([], limit=300):
    if "u" in (e.name or "") and "u" in (e.name or ""):
        nm = e.name.encode("unicode_escape").decode()
        if "0110" in nm or "1ea7" in nm or "1ea1" in nm:
            print(e.id, nm, "mien", repr(e.mien), "legacy", repr(e._lug_employee_legacy_mien()))
