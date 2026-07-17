# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

leaves = env["hr.leave"].sudo().search([("employee_id", "=", 56)], order="id desc")
print("total leaves:", len(leaves))
for lv in leaves[:10]:
    print(f"  {lv.id} state={lv.state} type={lv.holiday_status_id.name!r} val={lv.validation_type} from={lv.request_date_from}")
