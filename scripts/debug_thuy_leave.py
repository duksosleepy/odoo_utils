import json
leave = env["hr.leave"].search([
    ("employee_id.name", "ilike", "Cao Ngọc Nhi"),
    ("date_from", ">=", "2026-06-20"),
    ("date_from", "<", "2026-06-21"),
], limit=1, order="id desc")
thuy = env["res.users"].search([("name", "ilike", "thúy")], limit=5)
if not thuy:
    thuy = env["res.users"].search([("login", "ilike", "thuy")], limit=5)
out = {
    "leave": None,
    "thuy_users": [(u.id, u.login, u.name) for u in thuy],
}
if leave:
    emp = leave.employee_id
    out["leave"] = {
        "id": leave.id,
        "name": leave.name,
        "state": leave.state,
        "date_from": str(leave.date_from),
        "date_to": str(leave.date_to),
        "number_of_days": leave.number_of_days,
        "employee": emp.name,
        "employee_id": emp.id,
        "ma_bo_phan": emp.ma_bo_phan_id.name if emp.ma_bo_phan_id else None,
        "leave_manager": leave.employee_id.leave_manager_id.name if leave.employee_id.leave_manager_id else None,
        "first_approver": leave.first_approver_id.name if hasattr(leave, "first_approver_id") and leave.first_approver_id else None,
        "validation_type": leave.validation_type if hasattr(leave, "validation_type") else None,
        "holiday_status": leave.holiday_status_id.name,
    }
    for u in thuy[:1]:
        out["thuy"] = {
            "id": u.id,
            "login": u.login,
            "groups": [g.full_name for g in u.group_ids],
            "lug_enforced": u._lug_permission_is_enforced() if hasattr(u, "_lug_permission_is_enforced") else None,
            "visibility_policy": u.visibility_policy if hasattr(u, "visibility_policy") else None,
            "can_approve_lug": u.has_lug_permission("leave", "approve") if hasattr(u, "has_lug_permission") else None,
            "perm_map": dict(u._lug_effective_permission_map()) if hasattr(u, "_lug_effective_permission_map") else None,
        }
        try:
            leave.with_user(u).action_approve()
            out["approve_result"] = "OK"
        except Exception as e:
            out["approve_error"] = str(e)
            out["approve_error_type"] = type(e).__name__
with open(r"D:\Lap_odoo\lug_debug_thuy_leave.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=str)
