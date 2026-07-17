# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

from odoo.addons.hr_org_chart.controllers.hr_org_chart import HrOrgChartController

u85 = env["res.users"].browse(85)
Pub = env["hr.employee.public"].with_user(u85)
Emp = env["hr.employee"].with_user(u85)

print("=== 1. Real org chart controller for Cao (emp 8) ===")
ctrl = HrOrgChartController()
# emulate controller env: it uses request.env; we patch by calling internal logic via user env
# Reproduce _get_employee + get_org_chart core with u85 env
def get_employee(eid):
    e = Pub.with_context(allowed_company_ids=[1]).browse(eid)
    return e if e.has_access("read") else Pub.browse()

try:
    employee = get_employee(8)
    ancestors, current = Pub.sudo(), employee.sudo()
    current_parent = current.parent_id
    maxlvl = 6
    while current_parent and current != current_parent and employee.sudo() != current_parent and len(ancestors) < maxlvl:
        current = current_parent
        current_parent = current.parent_id
        if current_parent in ancestors:
            break
        ancestors += current
    # _prepare_employee_data for each (mix sudo ancestors + non-sudo employee)
    def prep(e):
        job = e.sudo().job_id
        return dict(id=e.id, name=e.name, job=job.name or "",
                    direct=len(e.child_ids - e), indirect=e.child_all_count)
    data = dict(self=prep(employee),
                managers=[prep(a) for a in ancestors],
                children=[prep(c) for c in employee.child_ids if c != employee])
    print("  OK org chart:", data["self"]["name"], "managers", [m["name"] for m in data["managers"]])
except Exception as ex:
    print("  FAIL", type(ex).__name__, str(ex)[:200])

print("\n=== 2. Security: anh.trinh must NOT read out-of-scope non-ref employees ===")
# emp outside VP and not a ref (e.g. a Nam employee with no link to anh.trinh)
nam = env["hr.employee"].sudo().search([("mien", "=", "Nam")], limit=5)
refs = set(env["hr.employee.access.mixin"]._hr_employee_access_reference_readable_ids(u85))
denied_ok = 0
leaked = []
for e in nam:
    if e.id in refs:
        continue
    try:
        Pub.browse(e.id).fetch(["name"])
        # if fetch succeeds it leaked
        leaked.append((e.id, e.name))
    except Exception:
        denied_ok += 1
print(f"  non-ref Nam employees correctly denied via fetch: {denied_ok}, leaked: {leaked}")

print("\n=== 3. VP scope intact ===")
print("  VP visible:", Pub.search_count([("mien", "=", "VP")]), "/ total VP", env["hr.employee"].sudo().search_count([("mien","=","VP")]))
print("  Nam visible (should be 0 + refs only):", Pub.search_count([("mien", "=", "Nam")]))

print("\n=== 4. emp 8 full form web_read + fetch all ===")
try:
    Emp.browse(8).read()
    print("  emp8 read() all OK")
except Exception as ex:
    print("  emp8 read() FAIL", str(ex)[:150])
try:
    Pub.browse(8).read()
    print("  public8 read() all OK")
except Exception as ex:
    print("  public8 read() FAIL", str(ex)[:150])
