# Check if assets bundle contains hr_leave_analytics
Att = env["ir.attachment"]
attachments = Att.search([
    ("name", "ilike", "web.assets_web"),
    ("type", "=", "binary"),
], order="write_date desc", limit=5)
print("attachments", len(attachments))
for att in attachments:
    print(att.name, att.write_date, att.file_size)

# Also check asset records via ir.asset model if exists
if "ir.asset" in env:
    assets = env["ir.asset"].search([("path", "ilike", "leave_analytics")])
    print("ir.asset leave_analytics", len(assets))
    for a in assets:
        print(a.path, a.bundle)

# Check module asset paths from manifest
import ast, os
manifest_path = os.path.join(
    env["ir.module.module"].search([("name", "=", "hr_leave_analytics")]).get_module_path(),
    "__manifest__.py",
)
with open(manifest_path) as f:
    manifest = ast.literal_eval(f.read())
print("manifest assets", manifest.get("assets", {}))
