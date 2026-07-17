# -*- coding: utf-8 -*-
import sys
from datetime import timedelta

sys.stdout.reconfigure(encoding="utf-8")

since = env.cr.now() - timedelta(days=3)
bot_handover = env.ref("business_discuss_bots.user_bot_handover").sudo()
bot_approval = env.ref("business_discuss_bots.user_bot_approval").sudo()
print("Handover bot partner:", bot_handover.partner_id.id, bot_handover.partner_id.name)
print("Approval bot partner:", bot_approval.partner_id.id, bot_approval.partner_id.name)

Message = env["mail.message"].sudo()
for label, partner in [("handover", bot_handover.partner_id), ("approval", bot_approval.partner_id)]:
    msgs = Message.search(
        [
            ("create_date", ">=", since),
            ("author_id", "=", partner.id),
        ],
        order="id desc",
        limit=10,
    )
    print(f"\n{label} bot messages (author) last 3d: {len(msgs)}")
    for m in msgs:
        print(f"  {m.id} {m.create_date} model={m.model} res={m.res_id} body_snip={m.body[:120] if m.body else ''}")

# Try manual handover notify on leave 397
lv = env["hr.leave"].sudo().browse(397)
if lv.exists():
    print("\n--- Manual test handover notify leave 397 ---")
    print("recipient user:", lv.handover_employee_ids.user_id.mapped("login"))
    try:
        lv._notify_handover_recipients_submit_via_bot()
        env.cr.commit()
        print("OK: _notify_handover_recipients_submit_via_bot completed")
    except Exception as ex:
        print("FAIL:", ex)
        import traceback
        traceback.print_exc()

    msgs2 = Message.search(
        [
            ("create_date", ">=", since),
            ("author_id", "=", bot_handover.partner_id.id),
            ("body", "ilike", "397"),
        ],
        limit=5,
    )
    print("Messages after manual notify:", len(msgs2))
