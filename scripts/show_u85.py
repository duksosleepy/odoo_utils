import sys
sys.stdout.reconfigure(encoding='utf-8')
u = env["res.users"].sudo().browse(85)
print("employee_mien", u.employee_mien, "visibility", u.visibility_policy, "lug_scope", u.lug_data_scope)
print("edit policy", u.lug_hr_employee_edit_policy, "zones", u.lug_hr_employee_edit_mien_zone_ids.mapped("legacy_mien"))
