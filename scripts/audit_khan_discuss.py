# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

Member = env["discuss.channel.member"].sudo()
user = env["res.users"].sudo().search([("login", "=", "khan.nguyen@sangtam.com")], limit=1)
if user:
    mems = Member.search([("partner_id", "=", user.partner_id.id)])
    print(f"All channels for khan.nguyen ({len(mems)}):")
    for m in mems.sorted(lambda x: -x.message_unread_counter):
        if m.message_unread_counter or m.channel_id.id in (168, 213):
            ch = m.channel_id
            bot_names = [p.name for p in ch.channel_member_ids.partner_id if "OdooBot" in (p.name or "")]
            print(
                f"  ch={ch.id} type={ch.channel_type} unread={m.message_unread_counter} "
                f"pinned={m.is_pinned} bots={bot_names} name={ch.name}"
            )

# Compare with working case phuong.nguyen
user2 = env["res.users"].sudo().search([("login", "=", "phuong.nguyen@sangtam.com")], limit=1)
if user2:
    mems = Member.search([("partner_id", "=", user2.partner_id.id), ("message_unread_counter", ">", 0)])
    print(f"\nUnread channels phuong.nguyen:")
    for m in mems:
        print(f"  ch={m.channel_id.id} unread={m.message_unread_counter} pinned={m.is_pinned}")
