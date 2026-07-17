# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

u = env["res.users"].browse(85)
for lv_id in [41, 42]:
    lv = env["hr.leave"].sudo().browse(lv_id)
    emp = lv.employee_id
    print(f"leave {lv_id}: emp {emp.id} {emp.name} mien {emp.mien}")
    print("  leave_manager", emp.leave_manager_id.login if emp.leave_manager_id else None)
    print("  approval_actionable", lv.approval_actionable_user_ids.mapped("login"))
    print("  responsible_lines", lv.responsible_approval_line_ids.mapped("user_id.login"))
    print("  handover", lv.handover_employee_ids.mapped("user_id.login"))

# Test rule 214 alone
rule214 = env.ref("hr_employee_hrm_detail.hr_leave_peer_read_rule", raise_if_not_found=False)
if rule214:
    dom = rule214._compute_domain("hr.leave", "read")
    print("\nrule 214 domain", dom)
    for lv_id in [41, 42]:
        ok = bool(env["hr.leave"].sudo().browse(lv_id).filtered_domain(dom))
        print(f"  leave {lv_id} passes 214:", ok)

rule213 = env.ref("hr_leave_type_mien.hr_leave_mien_scope_rule", raise_if_not_found=False)
if rule213:
    dom = rule213.with_user(u)._compute_domain("hr.leave", "read")
    print("\nrule 213 domain as user", dom)
