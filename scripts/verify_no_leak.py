# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
Pub = env["hr.employee.public"].with_user(u85)
Emp = env["hr.employee"].with_user(u85)

print("=== Real enforcement check for out-of-scope non-ref emp 4 (Nam) ===")
for label, M in [("public", Pub), ("employee", Emp)]:
    # fresh env each time to avoid cache from prior fetch
    rec = M.browse(4)
    # check_access
    try:
        rec.check_access("read")
        print(f"  [{label}] check_access -> ALLOWED (LEAK!)")
    except Exception:
        print(f"  [{label}] check_access -> denied OK")
    # read
    try:
        r = rec.read(["name"])
        print(f"  [{label}] read -> {r} (LEAK if name present!)")
    except Exception as ex:
        print(f"  [{label}] read -> denied OK ({type(ex).__name__})")
    # attribute access of name (the real data exposure)
    try:
        n = M.browse(4).name
        # if name is a real string -> leak; if False/empty under access fail
        print(f"  [{label}] .name -> {n!r}")
    except Exception as ex:
        print(f"  [{label}] .name -> blocked ({type(ex).__name__})")

print("\n=== Confirm emp 4 not in any search/listing ===")
print("  public search id=4:", bool(Pub.search([("id","=",4)], limit=1)))
print("  employee search id=4:", bool(Emp.search([("id","=",4)], limit=1)))

print("\n=== Re-confirm Cao (emp 8) fully readable ===")
print("  public read:", Pub.browse(8).read(["name"]))
print("  .name:", Pub.browse(8).name)
print("  parent .name via attr:", Pub.browse(8).parent_id.name)
