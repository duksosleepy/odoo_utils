# -*- coding: utf-8 -*-
from odoo.exceptions import MissingError

u = env["res.users"].browse(85)
lv = env["hr.leave"].with_user(u).browse(41)
LeaveModel = env["hr.leave"]
cls = LeaveModel.__class__.mro()[0]
print("class", cls.__name__)
print("enforced", u._lug_permission_is_enforced())
spec = {"employee_id": {"fields": {"display_name": {}}}}
try:
    val = cls._lug_leave_employee_web_value(
        LeaveModel,
        51,
        spec["employee_id"],
        env["hr.employee.public"].with_user(u),
    )
    print("employee value", val)
except Exception as ex:
    print("emp value err", type(ex).__name__, ex)

try:
    res = lv.web_read(spec)
    print("bound web_read ok id", res[0].get("employee_id", {}).get("id"))
except Exception as ex:
    print("bound web_read err", type(ex).__name__)
