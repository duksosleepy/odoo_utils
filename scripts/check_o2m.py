# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
Emp = env["hr.employee"].with_user(u85)

o2m_fields = [f for f, fld in Emp._fields.items() if fld.type in ("one2many", "many2many")]
print("o2m count", len(o2m_fields))
for eid in [8, 71]:
    print(f"\nemp {eid}")
    for fname in o2m_fields[:30]:
        field = Emp._fields[fname]
        if field.groups and not u85.has_groups(field.groups):
            continue
        try:
            Emp.browse(eid).web_read({fname: {"fields": {"display_name": {}}}})
        except Exception as ex:
            if "AccessError" in type(ex).__name__ or "employee" in str(ex).lower():
                print(" FAIL", fname, str(ex)[:180])
