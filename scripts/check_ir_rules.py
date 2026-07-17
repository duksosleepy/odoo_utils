# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
rules = env["ir.rule"].sudo().search([("model_id.model", "=", "hr.employee.public")])
print("rules count", len(rules))
for rule in rules:
    try:
        dom = rule._compute_domain("hr.employee.public", "read", u85)
        print(rule.name, dom)
        ok = bool(env["hr.employee.public"].sudo().search_count([("id", "=", 8)] + (dom if isinstance(dom, list) else [])))
        print("  emp8 passes rule", ok)
    except Exception as ex:
        print(rule.name, "ERR", ex)

# test comp_rule path used by ORM
rec8 = env["hr.employee.public"].with_user(u85).browse(8)
try:
    rec8._check_access_rule("read")
    print("check_access_rule OK")
except Exception as ex:
    print("check_access_rule FAIL", ex)

# Without lug - simulate old behavior: only employee_mien without zone widening
u = u85.sudo()
old_dom = [("mien", "=", u.employee_mien)]
print("old single mien domain", old_dom, "emp8", env["hr.employee.public"].sudo().search_count([("id","=",8)] + old_dom))
