url = env["ir.asset"]._get_asset_bundle_url(
    "web.assets_web.min.js",
    env["ir.asset"]._get_asset_bundle("web.assets_web", css=False, js=True).get_version(),
    {},
)
print("new asset url", url)
