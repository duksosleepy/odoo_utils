import json
emps = env["hr.employee"].search([("name", "ilike", "ngọc nhi")])
leaves = env["hr.leave"].search([("employee_id", "in", emps.ids)], order="id desc", limit=10)
out = {
    "employees": [(e.id, e.name) for e in emps],
    "leaves": [(l.id, l.name, l.state, str(l.request_date_from), str(l.request_date_to), l.number_of_days) for l in leaves],
}
with open(r"D:\Lap_odoo\lug_debug_nhi.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
