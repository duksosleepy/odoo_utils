# Force regenerate web.assets_web bundle
bundle = env["ir.qweb"]._get_asset_bundle("web.assets_web", css=False, js=True)
js_nodes = bundle.js()
print("js nodes count", len(js_nodes) if js_nodes else 0)
content = bundle.js().minify().content if bundle.js() else b""
text = content.decode("utf-8", errors="ignore") if content else ""
print("hr_leave_analytics_dashboard in new bundle:", "hr_leave_analytics_dashboard" in text)
