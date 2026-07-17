# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

lt = env["hr.leave.type"].sudo().browse(75)
print("Leave type:", lt.name, "validation:", lt.leave_validation_type)
for step in lt.multi_approval_step_ids.sorted("sequence"):
    print(
        f"  step {step.sequence} {step.name} "
        f"approver_user={step.approver_user_id.login if step.approver_user_id else 'NONE'} "
        f"emp1={step.leave_type_id.multi_step_approver_employee_1_id.name if step.sequence==1 else ''}"
    )
print("multi_step employees on type:")
for i in range(1, 7):
    emp = lt[f"multi_step_approver_employee_{i}_id"]
    if emp:
        print(f"  {i}: {emp.name} user={emp.user_id.login if emp.user_id else 'NONE'}")
