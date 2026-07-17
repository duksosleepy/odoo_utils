# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

for lid in [394, 396, 398]:
    lv = env["hr.leave"].sudo().browse(lid)
    print("=" * 50, f"Leave {lid}")
    print("employee:", lv.employee_id.name, "state:", lv.state)
    print("validation:", lv.validation_type, "multi_step_current:", lv.multi_step_current)
    step = lv._get_current_multi_step()
    if step:
        print("current step:", step.sequence, step.name, "approver:", step.approver_user_id.login)
    approvers = lv._get_multi_step_approvers()
    print("approvers:", approvers.mapped("login"))
    print("handover ready:", lv._handover_ready_for_approval())
