# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
Users = env["res.users"].with_user(u85)

for uid in [13, 76]:
    print(f"\n=== user {uid} with chatter ===")
    spec = {
        "name": {}, "login": {},
        "employee_id": {"fields": {"display_name": {}, "name": {}}},
        "message_ids": {"fields": {"body": {}, "author_id": {"fields": {"display_name": {}}}}},
        "activity_ids": {"fields": {"summary": {}, "user_id": {"fields": {"display_name": {}}}}},
    }
    try:
        r = Users.browse(uid).web_read(spec)
        print("OK messages", len(r[0].get("message_ids") or []))
    except Exception as ex:
        print("FAIL", type(ex).__name__, str(ex)[:400])
