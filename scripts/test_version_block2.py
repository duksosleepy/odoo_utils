# -*- coding: utf-8 -*-
user = env["res.users"].sudo().browse(58)
vp = env["hr.employee"].sudo().search([("mien", "=", "VP")], limit=1)
v = vp.version_id
print("version", v.id, "employee_id", v.employee_id.id)
print("related", v._lug_related_employees_for_profile_check().ids)

Version = env["hr.version"].with_user(user)
try:
    with env.cr.savepoint():
        Version.browse(v.id).write({"job_title": v.job_title or "x"})
        print("version write OK")
except Exception as e:
    print("version write BLOCKED", type(e).__name__)
