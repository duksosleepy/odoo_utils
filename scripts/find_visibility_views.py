views = env["ir.ui.view"].search([("model", "=", "res.users")])
legacy = []
lug = []
for v in views:
    arch = v.arch_db or v.arch or ""
    if 'name="employee_visibility"' in arch:
        legacy.append(v.name)
    if 'name="lug_permission"' in arch:
        lug.append(v.name)
mod_hrm = env["ir.module.module"].search([("name", "=", "hr_employee_hrm_detail")], limit=1)
mod_lug = env["ir.module.module"].search([("name", "=", "lug_permission")], limit=1)
print("hr_employee_hrm_detail version:", mod_hrm.latest_version)
print("lug_permission version:", mod_lug.latest_version)
print("legacy visibility views:", legacy or "(none)")
print("lug_permission views:", lug or "(none)")
