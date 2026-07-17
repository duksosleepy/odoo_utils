# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u = env["res.users"].browse(58)
UserPub = env["hr.employee.public"].with_user(u)
Emp = env["hr.employee"].with_user(u)

for eid in [2, 21, 33, 51, 52, 81]:
    e = env["hr.employee"].sudo().browse(eid)
    if not e.exists():
        continue
    print(f"\n=== emp {eid} {e.name} mien={e.mien} ===")
    try:
        UserPub.browse(eid).check_access("read")
        print("  public read OK")
    except Exception as ex:
        print("  public read FAIL", str(ex)[:100])
    try:
        Emp.browse(eid).check_access("write")
        print("  write OK")
    except Exception as ex:
        print("  write FAIL", str(ex)[:100])
    eu = Emp.browse(eid)
    print("  edit_allowed", eu._lug_is_employee_profile_edit_allowed())
    print("  readonly_ui", eu.employee_form_force_readonly_ui)
    try:
        eu.write({"work_phone": eu.work_phone or ""})
        print("  actual write OK")
    except Exception as ex:
        print("  actual write FAIL", type(ex).__name__, str(ex)[:120])

# Own form with parent
UserPub.browse(52)._hr_employee_read_is_restricted()
try:
    data = UserPub.browse(52).web_read({"name": {}, "parent_id": {"fields": {"display_name": {}}}})
    print("\nown form parent", data[0].get("parent_id"))
except Exception as ex:
    print("\nown form FAIL", str(ex)[:200])
