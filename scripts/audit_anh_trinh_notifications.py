# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

User = env["res.users"].sudo()
Leave = env["hr.leave"].sudo()
Message = env["mail.message"].sudo()
Member = env["discuss.channel.member"].sudo()

# --- anh.trinh profile ---
trinh = User.search([("login", "ilike", "anh.trinh%")], limit=1)
print("=" * 70)
print("USER anh.trinh")
if not trinh:
    print("NOT FOUND")
else:
    emp = trinh.employee_id
    print(f"  id={trinh.id} login={trinh.login} name={trinh.name}")
    print(f"  employee_id={emp.id if emp else None} name={emp.name if emp else '-'}")
    print(f"  job={emp.job_id.name if emp and emp.job_id else '-'} title={emp.job_title if emp else '-'}")
    print(f"  dept={emp.department_id.name if emp and emp.department_id else '-'}")
    print(f"  mien={emp.mien if emp else '-'}")
    print(f"  parent/manager={emp.parent_id.name if emp and emp.parent_id else '-'}")
    bot_h = env.ref("business_discuss_bots.user_bot_handover").partner_id
    bot_a = env.ref("business_discuss_bots.user_bot_approval").partner_id
    for label, bot in [("handover", bot_h), ("approval", bot_a)]:
        chs = env["discuss.channel"].sudo().search([
            ("channel_type", "=", "chat"),
            ("channel_member_ids.partner_id", "in", [trinh.partner_id.id, bot.id]),
        ])
        print(f"  {label} bot chats: {chs.ids}")
        for ch in chs[:3]:
            msgs = Message.search([
                ("model", "=", "discuss.channel"),
                ("res_id", "=", ch.id),
                ("author_id", "=", bot.id),
            ], order="id desc", limit=3)
            for m in msgs:
                print(f"    msg {m.id} {m.create_date}: {(m.body or '')[:120]}")

# --- Recent P leaves (like screenshot) ---
print("\n" + "=" * 70)
print("RECENT Nghỉ phép (P) LEAVES")
lt_p = env["hr.leave.type"].sudo().search([("name", "ilike", "Nghỉ phép (P)")], limit=1)
leaves = Leave.search(
    [("holiday_status_id", "=", lt_p.id), ("create_date", ">=", "2026-06-29")],
    order="id desc",
    limit=10,
)
for lv in leaves:
    emp = lv.employee_id
    print(f"\nLeave {lv.id} state={lv.state} validation={lv.validation_type}")
    print(f"  employee={emp.name if emp else 'NONE'} id={emp.id if emp else '-'} user={emp.user_id.login if emp and emp.user_id else '-'}")
    print(f"  display_name={lv.display_name}")
    print(f"  multi_step_current={lv.multi_step_current} handover_ready={lv._handover_ready_for_approval()}")
    print(f"  handover_to={lv.handover_employee_ids.mapped('name')}")
    print(f"  handover_states={lv.handover_acceptance_ids.mapped('state')}")
    step = lv._get_current_multi_step() if hasattr(lv, "_get_current_multi_step") else False
    if step:
        print(f"  current_step={step.sequence} {step.name} approver={step.approver_user_id.login if step.approver_user_id else 'NONE'}")
    approvers = lv._get_multi_step_approvers() if hasattr(lv, "_get_multi_step_approvers") else User.browse()
    print(f"  multi_step_approvers={[u.login for u in approvers]}")
    if trinh:
        print(f"  trinh_is_approver={trinh in approvers}")
        if lv.validation_type == "employee_hr_responsibles":
            lines = lv.responsible_approval_line_ids.filtered(lambda l: l.state == "pending")
            print(f"  responsible_pending={[(l.user_id.login, l.sequence) for l in lines[:5]]}")
            print(f"  trinh_in_responsible={trinh in lines.mapped('user_id')}")

# --- Leave type P multi-step config ---
print("\n" + "=" * 70)
print(f"LEAVE TYPE {lt_p.id} {lt_p.name} validation={lt_p.leave_validation_type}")
for step in lt_p.multi_approval_step_ids.sorted("sequence"):
    u = step.approver_user_id
    print(f"  step {step.sequence}: approver={u.login if u else 'NONE'} ({u.name if u else '-'})")

# --- Is anh.trinh approver on any step? ---
if trinh and lt_p:
    steps_with_trinh = lt_p.multi_approval_step_ids.filtered(lambda s: s.approver_user_id == trinh)
    print(f"\nanh.trinh assigned to steps: {steps_with_trinh.mapped('sequence')}")

# --- Manager chain for leave employees ---
print("\n" + "=" * 70)
print("MANAGER CHAIN (leave employees -> anh.trinh?)")
for lv in leaves[:4]:
    emp = lv.employee_id
    if not emp:
        continue
    chain = []
    cur = emp.parent_id
    while cur and len(chain) < 8:
        chain.append(f"{cur.name} ({cur.user_id.login if cur.user_id else 'no-user'})")
        cur = cur.parent_id
    print(f"  leave {lv.id} emp {emp.name}: chain={' -> '.join(chain) or 'empty'}")
