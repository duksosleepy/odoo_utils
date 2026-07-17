# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

trinh = env["res.users"].sudo().search([("login", "=", "anh.trinh@sangtam.com")], limit=1)
bot = env.ref("business_discuss_bots.user_bot_approval").partner_id
Message = env["mail.message"].sudo()

msgs = Message.search([
    ("author_id", "=", bot.id),
    ("create_date", ">=", "2026-06-29 06:00:00"),
], order="id desc", limit=10)
print(f"Recent approval bot msgs: {len(msgs)}")
for m in msgs:
    ch = env["discuss.channel"].sudo().browse(m.res_id)
    members = ch.channel_member_ids.mapped("partner_id.name")
    print(f"  {m.id} ch={m.res_id} members={members} body={(m.body or '')[:80]}")

lv394 = env["hr.leave"].sudo().browse(394)
print(f"\nLeave 394 step={lv394.multi_step_current}")
step = lv394._get_current_multi_step()
print(f"  step approver={step.approver_user_id.login if step and step.approver_user_id else 'NONE'}")
