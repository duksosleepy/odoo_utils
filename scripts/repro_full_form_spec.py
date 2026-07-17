# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u = env["res.users"].browse(85)
Emp = env["hr.employee"].with_user(u)

# Get full form view arch fields for hr.employee
view = env["hr.employee"].get_view(view_type="form")
arch = view.get("arch") or ""
import re
field_names = sorted(set(re.findall(r'<field[^>]+name="([^"]+)"', arch)))
print("form fields count", len(field_names))

# Build spec for all readable many2one fields
spec = {"display_name": {}}
Model = env["hr.employee"]
for fname in field_names:
    field = Model._fields.get(fname)
    if not field:
        continue
    if field.type == "many2one":
        spec[fname] = {"fields": {"display_name": {}}}
    elif field.type in ("char", "text", "boolean", "integer", "float", "selection", "date", "datetime"):
        spec[fname] = {}

print("spec keys", len(spec))

for eid in [88, 37, 90]:
    try:
        Emp.browse(eid).web_read(spec)
        print(f"full web_read {eid} OK")
    except Exception as ex:
        print(f"full web_read {eid} FAIL", type(ex).__name__, str(ex)[:250])
        # binary search - find offending field
        for fname in list(spec.keys()):
            try:
                Emp.browse(eid).web_read({fname: spec[fname]} if fname != "display_name" else {"display_name": {}})
            except Exception as ex2:
                if "88" in str(ex2) or "KeyError" in type(ex2).__name__:
                    print("  bad field", fname, str(ex2)[:100])
