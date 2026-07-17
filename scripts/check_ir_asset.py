# List all ir.asset for web.assets_backend
assets = env["ir.asset"].search([("bundle", "=", "web.assets_backend")], order="path")
print("total web.assets_backend ir.asset:", len(assets))
hr = assets.filtered(lambda a: "hr_leave" in (a.path or ""))
print("hr_leave related:", len(hr))
for a in hr[:10]:
    print(a.path)

# Check if module path exists on disk
import os
from odoo.modules.module import get_module_path
mp = get_module_path("hr_leave_analytics")
print("module path", mp)
js = os.path.join(mp, "static/src/dashboard/leave_analytics_dashboard.js")
print("js exists", os.path.exists(js))
