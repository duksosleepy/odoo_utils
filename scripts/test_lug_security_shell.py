user = env["res.users"].search([("login", "=", "admin")], limit=1)
print(env["lug.user.session"]._employee_org_snapshot(user))
