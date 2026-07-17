# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

Lt = env["hr.leave.type"].sudo()
trinh = env["res.users"].sudo().search([("login", "=", "anh.trinh@sangtam.com")], limit=1)
vp_types = Lt.search([("leave_validation_type", "in", ("multi_step_6", "employee_hr_responsibles"))])
print("VP-relevant leave types:")
for lt in vp_types:
    steps = lt.multi_approval_step_ids.sorted("sequence")
    approvers = [s.approver_user_id.login if s.approver_user_id else "-" for s in steps[:3]]
    print(
        f"  {lt.id} {lt.name!r} val={lt.leave_validation_type} "
        f"resp_source={lt.employee_responsible_source if lt.leave_validation_type == 'employee_hr_responsibles' else '-'} "
        f"steps={approvers}"
    )

# Khan parent chain with job titles
khan = env["hr.employee"].sudo().browse(56)
cur = khan
print(f"\nKhan chain:")
while cur:
    print(f"  {cur.name} job={cur.job_id.name!r} title={cur.job_title!r} user={cur.user_id.login if cur.user_id else '-'}")
    cur = cur.parent_id

# Who has holidays officer group
officers = env["hr.leave"].sudo().browse(400)._get_time_off_officer_users()
print(f"\nTime off officers (fallback): {officers.mapped('login')[:10]}")

# Can trinh multi_step approve any leave?
for lid in [400, 394]:
    lv = env["hr.leave"].sudo().browse(lid)
    print(f"leave {lid} can_multi_step_approve for trinh: ", end="")
    as_trinh = lv.with_user(trinh)
    as_trinh.invalidate_recordset(["can_multi_step_approve"])
    print(as_trinh.can_multi_step_approve)
