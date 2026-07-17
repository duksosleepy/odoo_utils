# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
Pub = env["hr.employee.public"].with_user(u85)
Emp = env["hr.employee"].with_user(u85)

print("=== child_ids / subordinate of emp 8 (Cao) ===")
for model_label, M in [("public", Pub), ("employee", Emp)]:
    rec = M.browse(8)
    for label, fn in [
        ("child_ids", lambda: rec.child_ids.ids),
        ("child_count", lambda: rec.child_count),
        ("child_all_count", lambda: rec.child_all_count),
        ("parent child_ids (89)", lambda: M.browse(89).child_ids.mapped("name")),
    ]:
        try:
            r = fn()
            print(f"  [{model_label}] OK {label}: {str(r)[:80]}")
        except Exception as ex:
            print(f"  [{model_label}] FAIL {label}: {type(ex).__name__} {str(ex)[:140]}")

print("\n=== simulate /hr/get_org_chart for emp 8 ===")
# Faithful to controller logic
Employee = Pub.with_context(allowed_company_ids=[1])
employee = Employee.browse(8)
print("has_access read emp8:", employee.has_access("read"))
ancestors, current = Pub.sudo(), employee.sudo()
current_parent = current.parent_id
maxlvl = 6
walk = []
while current_parent and current != current_parent and employee.sudo() != current_parent and len(ancestors) < maxlvl:
    current = current_parent
    current_parent = current.parent_id
    if current_parent in ancestors:
        break
    ancestors += current
    walk.append(current.id)
print("ancestors walked (sudo):", walk)
# children read is NON-sudo:
try:
    kids = [c.id for c in employee.child_ids if c != employee]
    print("children non-sudo ids:", kids)
    for c in employee.child_ids:
        _ = c.name  # _prepare_employee_data reads name non-sudo
    print("children name read OK")
except Exception as ex:
    print("children read FAIL", type(ex).__name__, str(ex)[:160])

print("\n=== is_subordinate compute (depends on user's employee subordinate_ids) ===")
try:
    print("emp8.is_subordinate:", Emp.browse(8).is_subordinate)
except Exception as ex:
    print("is_subordinate FAIL", type(ex).__name__, str(ex)[:160])
