# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

Notification = env["mail.notification"].sudo()
Message = env["mail.message"].sudo()

for mid in [3432, 3205, 3440]:
    m = Message.browse(mid)
    notifs = Notification.search([("mail_message_id", "=", mid)])
    print(f"msg {mid} notifications={len(notifs)}")
    for n in notifs:
        p = n.res_partner_id
        u = env["res.users"].search([("partner_id", "=", p.id)], limit=1)
        print(f"  partner={p.name} login={u.login if u else '-'} is_read={n.is_read} notification_type={n.notification_type}")

# User khan.nguyen unread notifications
user = env["res.users"].sudo().search([("login", "=", "khan.nguyen@sangtam.com")], limit=1)
if user:
    notifs = Notification.search(
        [
            ("res_partner_id", "=", user.partner_id.id),
            ("is_read", "=", False),
        ],
        order="id desc",
        limit=10,
    )
    print(f"\nUnread notifications for khan.nguyen: {len(notifs)}")
    for n in notifs:
        print(f"  {n.id} type={n.notification_type} msg={n.mail_message_id.id} model={n.mail_message_id.model}")
