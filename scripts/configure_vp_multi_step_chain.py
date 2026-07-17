# -*- coding: utf-8 -*-
"""Assign VP multi-step approvers steps 2-6 and notify stuck leave 394."""
import sys
sys.stdout.reconfigure(encoding="utf-8")

User = env["res.users"].sudo()
trinh = User.search([("login", "=", "anh.trinh@sangtam.com")], limit=1)
huong = User.search([("login", "=", "huong.dao@sangtam.com")], limit=1)
lug = User.search([("login", "=", "admin.lug@sangtam.com")], limit=1)

chain = [trinh, huong, lug, lug, lug, lug]  # steps 1-6
vp_multi = env["hr.leave.type"].sudo().search([("leave_validation_type", "=", "multi_step_6")])
for lt in vp_multi:
    for seq, user in enumerate(chain, start=1):
        if not user:
            continue
        step = lt.multi_approval_step_ids.filtered(lambda s: s.sequence == seq)[:1]
        if step:
            step.write({"approver_user_id": user.id})
    print(f"LT {lt.id} {lt.name}: steps configured")

env.cr.commit()

lv = env["hr.leave"].sudo().browse(394)
print(f"Leave 394 step={lv.multi_step_current} approver={lv._get_multi_step_approvers().mapped('login')}")
lv._notify_multi_step_current_turn_via_approval_bot()
env.cr.commit()
print("Notified leave 394")
