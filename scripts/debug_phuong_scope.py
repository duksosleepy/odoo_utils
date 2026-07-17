import json
u = env["res.users"].browse(57)
emp = env["hr.employee"].browse(4)
phuong_emp = u.employee_id
out = {
    "user": {
        "id": u.id,
        "login": u.login,
        "lug_data_scope": u.lug_data_scope,
        "visibility_policy": u.visibility_policy,
        "lug_enforced": u._lug_permission_is_enforced(),
        "assigned_ma_bo_phan": [(c.id, c.name, getattr(c, "code", None)) for c in u.assigned_ma_bo_phan_ids],
        "employee_ma_bo_phan": phuong_emp.ma_bo_phan_id.name if phuong_emp and phuong_emp.ma_bo_phan_id else None,
        "employee_store": phuong_emp.store_id.name if phuong_emp and hasattr(phuong_emp, "store_id") and phuong_emp.store_id else None,
    },
    "target_employee": {
        "id": emp.id,
        "name": emp.name,
        "ma_bo_phan": emp.ma_bo_phan_id.name if emp.ma_bo_phan_id else None,
        "ma_bo_phan_id": emp.ma_bo_phan_id.id if emp.ma_bo_phan_id else None,
        "store": emp.store_id.name if hasattr(emp, "store_id") and emp.store_id else None,
        "store_id": emp.store_id.id if hasattr(emp, "store_id") and emp.store_id else None,
        "mien": emp.mien if hasattr(emp, "mien") else None,
    },
}
# visibility domain
Mixin = env["hr.employee.access.mixin"]
out["policy_domain"] = str(Mixin.with_user(57)._hr_employee_policy_domain())
out["read_domain"] = str(Mixin.with_user(57)._hr_employee_visibility_read_domain(model_name="hr.employee"))
out["can_read_emp4"] = bool(env["hr.employee"].with_user(57).browse(4).exists())
out["all_employees_as_phuong"] = env["hr.employee"].with_user(57).search([]).mapped(lambda e: {
    "id": e.id, "name": e.name,
    "ma_bo_phan": e.ma_bo_phan_id.name if e.ma_bo_phan_id else None,
    "store": e.store_id.name if hasattr(e, "store_id") and e.store_id else None,
})
with open(r"D:\Lap_odoo\lug_debug_scope.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=str)
