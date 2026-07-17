# Get bundle version/hash from attachments
atts = env["ir.attachment"].search([
    ("url", "ilike", "/web/assets/%web.assets_web.min.js"),
], order="write_date desc", limit=3)
for att in atts:
    print(att.url, att.write_date)
