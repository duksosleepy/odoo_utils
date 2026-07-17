# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

User = env["res.users"].sudo()
Leave = env["hr.leave"].sudo()
Lt = env["hr.leave.type"].sudo()

trinh = User.search([("login", "=", "anh.trinh@sangtam.com")], limit=1)
print("anh.trinh:", trinh.id, trinh.name, "emp", trinh.employee_id.id)

# Find P leave type by id 75 from prior audit
for lt_id in [75, 76, 77, 78, 79, 80]:
    lt = Lt.browse(lt_id)
    if lt.exists():
        print(f"LT {lt_id}: {lt.name!r} validation={lt.leave_validation_type}")

lt_p = Lt.browse(75)
print("\nSteps on LT 75:")
for step in lt_p.multi_approval_step_ids.sorted("sequence"):
    u = step.approver_user_id
    print(f"  step {step.sequence}: {u.login if u else 'NONE'}")

leaves = Leave.search([], order="id desc", limit=8)
print("\nLatest leaves:")
for lv in leaves:
    emp = lv.employee_id
    approvers = lv._get_multi_step_approvers() if lv.validation_type == "multi_step_6" else User.browse()
    trinh_approver = trinh in approvers if trinh and approvers else False
    trinh_handover = trinh.employee_id in lv.handover_employee_ids if trinh and trinh.employee_id else False
    print(
        f"  {lv.id} emp={emp.name if emp else 'NONE'} type={lv.holiday_status_id.name} "
        f"val={lv.validation_type} step={lv.multi_step_current} state={lv.state} "
        f"handover={lv.handover_employee_ids.mapped('name')} h_states={lv.handover_acceptance_ids.mapped('state')} "
        f"approvers={[u.login for u in approvers]} trinh_approver={trinh_approver} trinh_handover={trinh_handover}"
    )

# Check if trinh is step approver on type 75
if trinh:
    assigned = lt_p.multi_approval_step_ids.filtered(lambda s: s.approver_user_id == trinh)
    print(f"\nTrinh on LT75 steps: {assigned.mapped('sequence')}")

# Org: who reports to trinh?
reports = env["hr.employee"].sudo().search([("parent_id", "=", trinh.employee_id.id)])
print(f"\nDirect reports to Trinh ({len(reports)}):", reports.mapped("name")[:10])

# Is trinh manager of khan/thanh?
for eid in [56, 71]:  # khan, thanh from prior
    e = env["hr.employee"].sudo().browse(eid)
    if e.exists():
        chain = []
        cur = e
        for _ in range(6):
            if not cur:
                break
            chain.append(cur.name)
            cur = cur.parent_id
        print(f"  chain from {e.name}: {' -> '.join(chain)}")
