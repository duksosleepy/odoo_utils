assets = env["ir.asset"].search([("path", "ilike", "time_off")], limit=5)
print("sample count", len(assets))
for asset in assets:
    print(asset.path, asset.bundle)
