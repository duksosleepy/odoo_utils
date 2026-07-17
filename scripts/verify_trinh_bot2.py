# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

trinh = env["res.users"].sudo().search([("login", "=", "anh.trinh@sangtam.com")], limit=1)
bot_a = env.ref("business_discuss_bots.user_bot_approval").partner_id
Message = env["mail.message"].sudo()
Member = env["discuss.channel.member"].sudo()

mems = Member.search([("partner_id", "=", trinh.partner_id.id)])
unread = []
for m in mems:
    if m.message_unread_counter:
        unread.append((m.channel_id.id, m.message_unread_counter, m.channel_id.name))
print("Unread channels for trinh:", unread[:10])

# Find chat with approval bot
chs = env["discuss.channel"].sudo().search([
    ("channel_type", "=", "chat"),
    ("channel_member_ids.partner_id", "in", [trinh.partner_id.id, bot_a.id]),
], limit=5)
for ch in chs:
    msgs = Message.search([
        ("model", "=", "discuss.channel"),
        ("res_id", "=", ch.id),
        ("author_id", "=", bot_a.id),
    ], order="id desc", limit=5)
    print(f"\nApproval chat {ch.id}: {len(msgs)} bot msgs")
    for msg in msgs:
        print(f"  {msg.id} {msg.create_date}: {(msg.body or '')[:100]}")

# Force notify leave 400
lv = env["hr.leave"].sudo().browse(400)
print(f"\nForce notify leave 400 approvers={lv._get_multi_step_approvers().mapped('login')}")
lv._notify_multi_step_current_turn_via_approval_bot()
env.cr.commit()

msgs2 = Message.search([
    ("author_id", "=", bot_a.id),
    ("body", "ilike", "Khan"),
], order="id desc", limit=3)
print(f"Msgs mentioning Khan: {len(msgs2)}")
for m in msgs2:
    print(f"  {m.id} {m.create_date}")
