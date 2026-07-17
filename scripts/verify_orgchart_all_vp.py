# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
Pub = env["hr.employee.public"].with_user(u85)

def _get_employee(eid):
    e = Pub.with_context(allowed_company_ids=[1]).browse(eid)
    return e if e.has_access("read") else Pub.browse()

def _prepare_employee_data(employee):
    # EXACT copy of controller logic
    job = employee.sudo().job_id
    return dict(
        id=employee.id,
        name=employee.name,
        job_id=job.id,
        job_name=job.name or "",
        direct_sub_count=len(employee.child_ids - employee),
        indirect_sub_count=employee.child_all_count,
        write_date=int(employee.write_date.timestamp() * 1000) if employee.write_date else 0,
    )

def get_org_chart(employee_id):
    employee = _get_employee(employee_id)
    if not employee:
        return {"managers": [], "children": []}
    ancestors, current = Pub.sudo(), employee.sudo()
    current_parent = current.parent_id
    max_level = 6
    while current_parent and current != current_parent and employee.sudo() != current_parent and len(ancestors) < max_level:
        current = current_parent
        current_parent = current.parent_id
        if current_parent in ancestors:
            break
        ancestors += current
    values = dict(
        self=_prepare_employee_data(employee),
        managers=[_prepare_employee_data(a) for idx, a in enumerate(ancestors) if idx < max_level - 1],
        children=[_prepare_employee_data(c) for c in employee.child_ids if c != employee],
    )
    values["managers"].reverse()
    return values

# Test every VP employee that has a manager (these are the ones that failed)
vp = env["hr.employee"].sudo().search([("mien", "=", "VP")])
print(f"Testing org chart for {len(vp)} VP employees as anh.trinh:\n")
fails = []
for e in vp:
    try:
        res = get_org_chart(e.id)
        mgr = [m["name"] for m in res["managers"]]
        print(f"  OK  emp {e.id:>3} {e.name:<22} managers={mgr}")
    except Exception as ex:
        fails.append((e.id, e.name, type(ex).__name__, str(ex)[:90]))
        print(f"  FAIL emp {e.id:>3} {e.name:<22} {type(ex).__name__} {str(ex)[:90]}")

print(f"\nTotal FAILS: {len(fails)}")
