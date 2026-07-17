# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
Pub = env["hr.employee.public"].with_user(u85)
Emp = env["hr.employee"].with_user(u85)
mixin = env["hr.employee.access.mixin"]

refs = set(mixin._hr_employee_access_reference_readable_ids(u85))
print("89 in refs", 89 in refs)
print("policy domain", mixin._hr_employee_policy_domain(u85))

print("\n--- emp 89 (parent of Cao Thi Trang) via hr.employee.public ---")
p89 = Pub.browse(89)
for label, fn in [
    ("check_access", lambda: p89.check_access("read")),
    ("search visible", lambda: bool(Pub.search([("id","=",89)], limit=1))),
    ("read name", lambda: p89.read(["name"])),
    ("web_read name", lambda: p89.web_read({"name": {}, "display_name": {}})),
    ("get_avatar_card_data", lambda: p89.get_avatar_card_data(["display_name", "job_title"])),
    ("read avatar_128", lambda: p89.read(["avatar_128"])),
    ("web_read avatar", lambda: p89.web_read({"avatar_128": {}, "display_name": {}})),
]:
    try:
        r = fn()
        print(f"  OK {label}: {str(r)[:60]}")
    except Exception as ex:
        print(f"  FAIL {label}: {type(ex).__name__} {str(ex)[:120]}")

print("\n--- emp 89 via hr.employee ---")
e89 = Emp.browse(89)
for label, fn in [
    ("check_access", lambda: e89.check_access("read")),
    ("read name", lambda: e89.read(["name"])),
    ("web_read name", lambda: e89.web_read({"name": {}, "display_name": {}})),
    ("get_avatar_card_data", lambda: e89.get_avatar_card_data(["display_name", "job_title"])),
]:
    try:
        r = fn()
        print(f"  OK {label}: {str(r)[:60]}")
    except Exception as ex:
        print(f"  FAIL {label}: {type(ex).__name__} {str(ex)[:120]}")

print("\n--- open Cao Thi Trang form: parent avatar read ---")
# The many2one_avatar_employee widget reads the related public record
try:
    r = Emp.browse(8).web_read({
        "name": {},
        "parent_id": {"fields": {"display_name": {}, "avatar_128": {}}},
        "coach_id": {"fields": {"display_name": {}, "avatar_128": {}}},
    })
    print("  OK parent web_read:", r[0].get("parent_id"))
except Exception as ex:
    print("  FAIL", type(ex).__name__, str(ex)[:200])
