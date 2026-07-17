# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

trinh = env["res.users"].sudo().search([("login", "=", "anh.trinh@sangtam.com")], limit=1)
env_trinh = env(user=trinh.id)

for lid in [400, 398, 396, 394]:
    lv = env["hr.leave"].sudo().browse(lid)
    try:
        as_trinh = env_trinh["hr.leave"].browse(lid)
        emp_name = as_trinh.employee_id.name
        emp_display = as_trinh.employee_id.display_name
    except Exception as ex:
        emp_name = f"ERR:{ex}"
        emp_display = emp_name
    print(f"leave {lid} real_emp={lv.employee_id.name} as_trinh_reads={emp_name!r} display={emp_display!r}")

# org chart approvers if responsibles mode
lv = env["hr.leave"].sudo().browse(400)
if hasattr(lv, "_get_responsible_approval_users"):
    users = lv._get_responsible_approval_users()
    print(f"\nleave 400 org-chart approvers: {users.mapped('login')}")
    print(f"trinh in chain: {trinh in users}")

# VP mien config
cfg = env["hr.leave.mien.config"].sudo().search([("mien", "=", "VP")], limit=1)
if cfg:
    print(f"\nVP config leave types: {cfg.leave_type_ids.mapped('name')}")

# Who should be step 1 for VP? Check HCNS dept employees as approver pool
lt = env["hr.leave.type"].sudo().browse(75)
dept = lt.multi_step_hr_source_department_id
print(f"\nLT75 HR dept: {dept.name if dept else 'NONE'}")
if dept:
    emps = env["hr.employee"].sudo().search([("department_id", "child_of", dept.id), ("user_id", "!=", False)])
    print(f"  pool users ({len(emps)}):", emps.mapped("user_id").mapped("login")[:15])
