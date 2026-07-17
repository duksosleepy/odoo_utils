import json
leaves = env["hr.leave"].search([
    ("employee_id.name", "ilike", "Cao Ngọc Nhi"),
], order="id desc", limit=10)
thuy = env["res.users"].browse(17)
out = {
    "leaves": [{
        "id": l.id,
        "name": l.name,
        "state": l.state,
        "date_from": str(l.date_from),
        "date_to": str(l.date_to),
        "number_of_days": l.number_of_days,
        "request_date_from": str(l.request_date_from) if l.request_date_from else None,
        "request_date_to": str(l.request_date_to) if l.request_date_to else None,
        "holiday_status": l.holiday_status_id.name,
    } for l in leaves],
}
leave = leaves.filtered(lambda l: l.state in ("confirm", "validate1"))[:1]
if not leave:
    leave = leaves[:1]
if leave:
    l = leave
    out["target_leave_id"] = l.id
    try:
        l.with_user(thuy).action_approve()
        out["approve"] = "OK"
    except Exception as e:
        out["approve_error"] = str(e)
        out["approve_type"] = type(e).__name__
with open(r"D:\Lap_odoo\lug_debug_thuy_leave2.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=str)
