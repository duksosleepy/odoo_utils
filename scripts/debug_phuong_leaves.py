import json
u = env["res.users"].browse(57)
emp4 = env["hr.employee"].browse(4)
leaves = env["hr.leave"].with_user(57).search([])
out = {
    "emp4_leave_manager": emp4.leave_manager_id.id if emp4.leave_manager_id else None,
    "emp4_leave_manager_name": emp4.leave_manager_id.name if emp4.leave_manager_id else None,
    "phuong_user_id": u.id,
    "phuong_employee_id": u.employee_id.id,
    "leave_count": len(leaves),
    "leave_employees": leaves.mapped(lambda l: {
        "leave_id": l.id,
        "emp_id": l.employee_id.id,
        "emp_name": l.employee_id.name,
        "ma_bo_phan": l.employee_id.ma_bo_phan_id.name if l.employee_id.ma_bo_phan_id else None,
    }),
    "approval_emp_ids": env["hr.employee.access.mixin"].with_user(57)._hr_employee_leave_approval_emp_ids(),
}
with open(r"D:\Lap_odoo\lug_debug_leaves.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=str)
