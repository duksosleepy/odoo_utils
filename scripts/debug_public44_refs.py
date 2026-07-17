# -*- coding: utf-8 -*-
u = env["res.users"].sudo().browse(85)
Leave = env["hr.leave"].with_user(u)
leaves = Leave.search([])
print("leaves count", len(leaves))
emp_ids = set(leaves.mapped("employee_id").ids)
print("leave employee ids", sorted(emp_ids))

UserPub = env["hr.employee.public"].with_user(u)
for eid in sorted(emp_ids):
    ok = bool(UserPub.search([("id", "=", eid)]))
    print(" emp", eid, "public readable", ok)

# leaves referencing emp 44 specifically
l44 = Leave.search([("employee_id", "=", 44)])
print("leaves for emp 44", len(l44), l44.ids[:5])

# who references 44 as parent/coach
Emp = env["hr.employee"].sudo()
refs = Emp.search(["|", ("parent_id", "=", 44), ("coach_id", "=", 44)])
print("parent/coach refs", refs.ids)

visible = UserPub.search([])
print("visible public ids", visible.ids)

missing = [eid for eid in emp_ids if eid not in visible.ids]
print("leave emps NOT in public visible", missing)
