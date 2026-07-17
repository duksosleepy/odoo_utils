import json
import base64

Dashboard = env["spreadsheet.dashboard"].search(
    [("name", "=", "Báo cáo tổng nghỉ phép")], limit=1
)
if not Dashboard:
    print("Dashboard not found")
else:
    raw = Dashboard.spreadsheet_raw or Dashboard.spreadsheet_data
    if isinstance(raw, str):
        data = json.loads(raw)
    else:
        data = raw
    filters = data.get("globalFilters", [])
    print("filters:", [(f.get("type"), f.get("label")) for f in filters])
    print("has_text", any(f.get("type") == "text" for f in filters))
