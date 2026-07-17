# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
u = env["res.users"].browse(85)
Emp = env["hr.employee"].with_user(u)
for eid in [88, 37, 81]:
    e = Emp.browse(eid)
    print(eid, e.name, "mien", e.mien,
          "edit", e._lug_is_employee_profile_edit_allowed(),
          "readonly_ui", e.employee_form_force_readonly_ui)
try:
    Emp.browse(88).write({"work_phone": Emp.browse(88).work_phone or "x"})
    print("write 88 OK")
except Exception as ex:
    print("write 88 FAIL", str(ex)[:120])
