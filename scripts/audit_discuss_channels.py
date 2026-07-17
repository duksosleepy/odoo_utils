# -*- coding: utf-8 -*-
import sys
from datetime import timedelta

sys.stdout.reconfigure(encoding="utf-8")

Leave = env["hr.leave"].sudo()
Message = env["mail.message"].sudo()
Channel = env["discuss.channel"].sudo()
since = env.cr.now() - timedelta(days=1)

for lid in [397, 46, 394, 396, 398]:
    lv = Leave.browse(lid)
    if not lv.exists():
        continue
    print("=" * 60)
    print(f"Leave {lid} create={lv.create_date} write={lv.write_date} state={lv.state}")
    for emp in lv.handover_employee_ids:
        u = emp.user_id
        if not u:
            print(f"  handover {emp.name}: NO USER")
            continue
        bot = env.ref("business_discuss_bots.user_bot_handover").partner_id
        ch = Channel.search(
            [
                ("channel_type", "=", "chat"),
                ("channel_member_ids.partner_id", "in", [u.partner_id.id, bot.id]),
            ],
            limit=5,
        )
        print(f"  handover recipient {u.login} channels={ch.ids}")
        for c in ch:
            msgs = Message.search(
                [
                    ("model", "=", "discuss.channel"),
                    ("res_id", "=", c.id),
                    ("create_date", ">=", lv.create_date),
                    ("author_id", "=", bot.id),
                ],
                order="id asc",
            )
            print(f"    channel {c.id}: {len(msgs)} bot msgs since leave create")
            for m in msgs:
                snip = (m.body or "")[:100].replace("\n", " ")
                print(f"      {m.create_date} {snip}")

    if lv.validation_type == "employee_hr_responsibles":
        pending = lv.responsible_approval_line_ids.filtered(lambda l: l.state == "pending")
        for line in pending[:2]:
            u = line.user_id
            bot = env.ref("business_discuss_bots.user_bot_approval").partner_id
            ch = Channel.search(
                [
                    ("channel_type", "=", "chat"),
                    ("channel_member_ids.partner_id", "in", [u.partner_id.id, bot.id]),
                ],
                limit=5,
            )
            print(f"  approver {u.login} channels={ch.ids}")
            for c in ch:
                msgs = Message.search(
                    [
                        ("model", "=", "discuss.channel"),
                        ("res_id", "=", c.id),
                        ("create_date", ">=", lv.create_date),
                        ("author_id", "=", bot.id),
                    ],
                    order="id asc",
                )
                print(f"    channel {c.id}: {len(msgs)} approval bot msgs since leave create")
                for m in msgs:
                    snip = (m.body or "")[:100].replace("\n", " ")
                    print(f"      {m.create_date} {snip}")
