# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

types = env["hr.leave.type"].sudo().search([("name", "ilike", "Nghỉ phép")])
for lt in types:
    steps_ok = lt.multi_approval_step_ids.filtered("approver_user_id")
    print(
        f"id={lt.id} {lt.name} validation={lt.leave_validation_type} "
        f"steps_with_approver={len(steps_ok)}/{len(lt.multi_approval_step_ids)}"
    )
