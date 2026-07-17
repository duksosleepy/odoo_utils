# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

leaves = env["hr.leave"].sudo().search([("holiday_status_id", "=", 75), ("state", "=", "confirm")])
print(f"P leaves confirm: {len(leaves)}")
for lv in leaves:
    print(f"  {lv.id} employee_id={lv.employee_id.id} name={lv.employee_id.name!r}")

# Configure step 1 = anh.trinh on all VP multi_step types
trinh = env["res.users"].sudo().search([("login", "=", "anh.trinh@sangtam.com")], limit=1)
vp_multi = env["hr.leave.type"].sudo().search([("leave_validation_type", "=", "multi_step_6")])
print(f"\nConfiguring step 1 approver={trinh.login} on {len(vp_multi)} types")
for lt in vp_multi:
    step1 = lt.multi_approval_step_ids.filtered(lambda s: s.sequence == 1)[:1]
    if step1:
        step1.sudo().write({"approver_user_id": trinh.id})
        print(f"  LT {lt.id} {lt.name}: step1 -> {trinh.login}")

env.cr.commit()

# Backfill approval bot for ready leaves
ready = leaves.filtered(lambda l: l._handover_ready_for_approval())
print(f"\nBackfill notify on {len(ready)} leaves: {ready.ids}")
for lv in ready:
    approvers = lv._get_multi_step_approvers()
    print(f"  leave {lv.id} approvers={[u.login for u in approvers]}")
    lv._notify_multi_step_current_turn_via_approval_bot()

env.cr.commit()
print("DONE")
