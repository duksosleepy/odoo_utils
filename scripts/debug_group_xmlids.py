import json
ids = [19, 33, 32, 29, 42, 1]
Imd = env["ir.model.data"].sudo()
rows = Imd.search([("model", "=", "res.groups"), ("res_id", "in", ids)])
out = {r.res_id: r.complete_name for r in rows}
out["groups"] = [(g.id, g.full_name) for g in env["res.groups"].browse(ids)]
with open(r"D:\Lap_odoo\lug_debug_group_xmlids.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
