# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

for eid in [8, 71]:
    e = env["hr.employee"].sudo().browse(eid)
    print(f"emp {eid}", {
        "name": e.name,
        "mien": e.mien,
        "active": e.active,
        "user_id": e.user_id.login if e.user_id else None,
        "employee_visibility": getattr(e, "employee_visibility", None),
        "parent_id": e.parent_id.id if e.parent_id else None,
        "parent_mien": e.parent_id.mien if e.parent_id else None,
        "ma_bo_phan": e.ma_bo_phan_id.code if getattr(e, "ma_bo_phan_id", False) else None,
    })

# Check if user 13 is special
u13 = env["res.users"].sudo().browse(13)
u76 = env["res.users"].sudo().browse(76)
u85 = env["res.users"].browse(85)
for u in [u13, u76]:
    vis = bool(env["res.users"].with_user(u85).search([("id","=",u.id)], limit=1))
    print("user", u.login, "readable by anh.trinh", vis, "active", u.active, "share", u.share)
