# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

def check_user(uid, label, expect_miens):
    u = env["res.users"].browse(uid)
    Pub = env["hr.employee.public"].with_user(u)
    print(f"\n=== {label} (id={uid}) scope={u.lug_data_scope} zones={u.lug_hr_employee_edit_mien_zone_ids.mapped('legacy_mien')} ===")
    for m in ["VP", "Nam", "Bắc", "ĐTT"]:
        tot = env["hr.employee"].sudo().search_count([("mien", "=", m)])
        vis = Pub.search_count([("mien", "=", m)])
        print(f"  {m}: visible {vis}/{tot}")
    # open a profile with a manager chain
    sample = env["hr.employee"].sudo().search([("mien", "in", expect_miens), ("parent_id", "!=", False)], limit=1)
    if sample:
        try:
            Pub.browse(sample.id).read()
            _ = Pub.browse(sample.id).parent_id.name
            print(f"  open {sample.name} (parent={sample.parent_id.name}) -> OK")
        except Exception as ex:
            print(f"  open {sample.name} -> FAIL {type(ex).__name__} {str(ex)[:120]}")

check_user(85, "anh.trinh (VP)", ["VP"])
check_user(58, "admin.lug (Nam/Bắc/ĐTT)", ["Nam", "Bắc", "ĐTT"])

# admin.miennam (user 8 -> emp 2)
u8 = env["res.users"].browse(8)
Pub8 = env["hr.employee.public"].with_user(u8)
print(f"\n=== admin.miennam (id=8) ===")
try:
    Pub8.browse(2).read()
    print("  own emp 2 read OK")
except Exception as ex:
    print("  emp2 FAIL", str(ex)[:120])
