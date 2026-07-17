# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
Users = env["res.users"].with_user(u85)

def test_user(uid):
    u = env["res.users"].sudo().browse(uid)
    print(f"\n=== user {uid} {u.login} emp={u.employee_id.id} ===")
    # can user list see them?
    print("in user search", bool(Users.search([("id", "=", uid)], limit=1)))
    try:
        Users.browse(uid).check_access("read")
        print("check_access OK")
    except Exception as ex:
        print("check_access FAIL", str(ex)[:200])
    
    Model = env["res.users"]
    spec = {}
    for fname, field in Model._fields.items():
        if field.type in ("one2many",):
            continue
        if field.groups and not u85.has_groups(field.groups):
            continue
        if field.type == "many2one" and fname == "employee_id":
            spec[fname] = {"fields": {"display_name": {}, "name": {}, "id": {}}}
        else:
            spec[fname] = {}
    print("spec size", len(spec))
    try:
        r = Users.browse(uid).web_read(spec)
        print("full web_read OK keys", len(r[0]) if r else 0)
    except Exception as ex:
        print("full web_read FAIL", type(ex).__name__, str(ex)[:400])

test_user(13)  # trang.cao
test_user(76)  # thanh.thach

# LUG user visibility
print("\nLUG enforced", u85.sudo()._lug_permission_is_enforced())
readable = Users.search([])
print("readable users count", len(readable))
for uid in [13, 76]:
    print(f"user {uid} readable", uid in readable.ids)
