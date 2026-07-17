# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

Message = env["mail.message"].sudo()
Channel = env["discuss.channel"].sudo()
Member = env["discuss.channel.member"].sudo()

msg_ids = [3432, 3396, 3426, 3440, 3222, 3208, 3205]
for mid in msg_ids:
    m = Message.browse(mid)
    if not m.exists():
        continue
    ch = Channel.browse(m.res_id) if m.model == "discuss.channel" else Channel.browse()
    members = Member.search([("channel_id", "=", ch.id)]) if ch else Member.browse()
    names = members.mapped("partner_id.name")
    logins = []
    for mem in members:
        u = env["res.users"].sudo().search([("partner_id", "=", mem.partner_id.id)], limit=1)
        if u:
            logins.append(u.login)
    print(f"msg {mid} ch={ch.id} create={m.create_date}")
    print(f"  members: {names}")
    print(f"  logins: {logins}")
    print(f"  body: {(m.body or '')[:150]}")
    print()

# Check discuss notification for phuong.nguyen
user = env["res.users"].sudo().search([("login", "=", "phuong.nguyen@sangtam.com")], limit=1)
if user:
    mems = Member.search([("partner_id", "=", user.partner_id.id), ("is_pinned", "=", True)])
    print(f"Pinned channels for {user.login}: {mems.mapped('channel_id.id')}")
    unread = mems.filtered(lambda m: m.message_unread_counter > 0)
    print(f"Unread pinned: {[(m.channel_id.id, m.message_unread_counter) for m in unread]}")
