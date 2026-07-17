paths = env["ir.asset"]._get_asset_paths("web.assets_backend", {})
matches = [p for p in paths if "leave_analytics" in p[0]]
print("matches in web.assets_backend:", len(matches))
for p in matches:
    print(p)

paths_web = env["ir.asset"]._get_asset_paths("web.assets_web", {})
matches_web = [p for p in paths_web if "leave_analytics" in p[0]]
print("matches in web.assets_web:", len(matches_web))
for p in matches_web:
    print(p)

installed = env["ir.asset"]._get_installed_addons_list()
print("hr_leave_analytics installed:", "hr_leave_analytics" in installed)
