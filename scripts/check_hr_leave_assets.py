mods = env["ir.module.module"].search([("name", "=", "hr_leave_analytics")])
print("state", mods.state, "version", mods.latest_version)
assets = env["ir.asset"].search([("path", "ilike", "hr_leave_analytics")])
print("ir.asset count", len(assets))
for asset in assets:
    print(asset.name, asset.path, asset.bundle)
