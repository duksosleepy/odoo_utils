# -*- coding: utf-8 -*-
import sys
from datetime import timedelta

sys.stdout.reconfigure(encoding="utf-8")

Leave = env["hr.leave"].sudo()
Message = env["mail.message"].sudo()
since = env.cr.now() - timedelta(days=3)
leaves = Leave.search(
    [("create_date", ">=", since), ("state", "in", ("confirm", "validate1", "validate"))],
    order="id desc",
    limit=15,
)
print(f"Recent leaves (last 3 days): {len(leaves)}\n")

bot_handover = env.ref("business_discuss_bots.user_bot_handover", raise_if_not_found=False)
bot_approval = env.ref("business_discuss_bots.user_bot_approval", raise_if_not_found=False)
print("Bot handover user:", bot_handover.login if bot_handover else "MISSING")
print("Bot approval user:", bot_approval.login if bot_approval else "MISSING")
print()

for lv in leaves:
    emp = lv.employee_id
    login = emp.user_id.login if emp and emp.user_id else "-"
    handover_emps = lv.handover_employee_ids
    acceptance = lv.handover_acceptance_ids
    print("=" * 70)
    print(
        f"Leave {lv.id} | {lv.display_name} | state={lv.state} | "
        f"employee={emp.name if emp else '-'} ({login})"
    )
    print(f"  skip_work_handover={lv.skip_work_handover}")
    print(f"  handover_employee_ids={handover_emps.ids} names={handover_emps.mapped('name')}")
    print(f"  acceptance lines={len(acceptance)} states={acceptance.mapped('state')}")
    try:
        ready = lv._handover_ready_for_approval()
        blocking = lv._get_handover_blocking_employees().mapped("name")
    except Exception as ex:
        ready = f"ERR {ex}"
        blocking = []
    print(f"  handover_ready_for_approval={ready} blocking={blocking}")
    print(f"  validation_type={lv.validation_type}")
    if lv.responsible_approval_line_ids:
        pending = lv.responsible_approval_line_ids.filtered(lambda l: l.state == "pending")
        print(
            f"  approval lines pending: "
            f"{[(l.user_id.login, l.sequence) for l in pending[:5]]}"
        )
    # discuss bot messages (last 3 days)
    markers = [f'data-oe-handover-leave="{lv.id}"']
    if lv.split_group_id:
        markers.append(f'data-oe-handover-split-group="{lv.split_group_id}"')
    domain = [("create_date", ">=", since)]
    if len(markers) == 1:
        domain.append(("body", "ilike", markers[0]))
    else:
        domain.extend(["|"] + [("body", "ilike", m) for m in markers])
    msgs = Message.search(domain, limit=5)
    print(f"  bot messages (handover/approval link): {len(msgs)}")
    for msg in msgs[:3]:
        author = msg.author_id.name if msg.author_id else "-"
        print(f"    - {msg.create_date} author={author} model={msg.model}")

# Test dispatch on latest confirm leave with handover
candidates = leaves.filtered(lambda l: l.handover_employee_ids and l.state == "confirm")
if candidates:
    lv = candidates[0]
    print("\n" + "=" * 70)
    print(f"DRY RUN notify check on leave {lv.id}")
    primaries = lv._collect_handover_submit_notify_primaries()
    print(f"  primaries from collect: {primaries.ids}")
    would_skip_approval = bool(lv.handover_employee_ids and not lv._handover_ready_for_approval())
    print(f"  approval notify skipped at submit (handover pending): {would_skip_approval}")
