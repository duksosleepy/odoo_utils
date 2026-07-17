# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from lxml import etree

u85 = env["res.users"].browse(85)
Users = env["res.users"].with_user(u85)

def fields_from_view(xmlid):
    view = env.ref(xmlid, raise_if_not_found=False)
    if not view:
        return []
    arch = etree.fromstring(view.arch_db.encode())
    names = []
    for node in arch.iter():
        if node.tag == "field" and node.get("name"):
            names.append(node.get("name"))
    return names

for uid in [13, 76]:
    u = env["res.users"].sudo().browse(uid)
    print(f"\n=== user {uid} {u.login} ===")
    for xmlid in ["base.view_users_form", "hr.res_users_view_form", "lug_permission.res_users_form_lug_permission"]:
        try:
            fnames = fields_from_view(xmlid)
            if fnames:
                print(xmlid, "fields", len(fnames))
        except Exception:
            pass
    
    spec = {"display_name": {}, "name": {}, "login": {}}
    spec["employee_id"] = {"fields": {"display_name": {}, "name": {}, "job_title": {}, "parent_id": {"fields": {"display_name": {}}}}}
    try:
        r = Users.browse(uid).web_read(spec)
        print("web_read employee_id OK", r[0].get("employee_id"))
    except Exception as ex:
        print("web_read FAIL", type(ex).__name__, str(ex)[:400])

# hr.employee form via hr.employee model
Emp = env["hr.employee"].with_user(u85)
for eid in [8, 71]:
    spec = {"name": {}, "parent_id": {"fields": {"display_name": {}, "name": {}}}, "coach_id": {"fields": {"display_name": {}}}}
    try:
        r = Emp.browse(eid).web_read(spec)
        print(f"hr.employee {eid} web_read OK parent={r[0].get('parent_id')}")
    except Exception as ex:
        print(f"hr.employee {eid} FAIL", str(ex)[:300])
