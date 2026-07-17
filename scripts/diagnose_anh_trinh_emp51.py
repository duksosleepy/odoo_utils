# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")

u = env["res.users"].sudo().search([("login", "=", "anh.trinh@sangtam.com")], limit=1)
print("=== USER ===")
print("id", u.id, "login", u.login)
print("employee_id", u.employee_id.id, u.employee_id.name if u.employee_id else None)
print("employee_mien", u.employee_mien)
print("lug_data_scope", u.lug_data_scope, "visibility_policy", u.visibility_policy)
print("lug_enforced", u._lug_permission_is_enforced())
print("edit_policy", u.lug_hr_employee_edit_policy)
print("edit_zones", u.lug_hr_employee_edit_mien_zone_ids.mapped("legacy_mien"))
print("allowed_edit_miens", u.lug_allowed_employee_edit_legacy_miens())
print("lug_groups", u.lug_group_ids.mapped("name"))
print("hr_perms", u._lug_effective_permission_map().get("hr", set()))

emp51 = env["hr.employee"].sudo().browse(51)
print("\n=== EMPLOYEE 51 ===")
if emp51.exists():
    print("name", emp51.name, "mien", emp51.mien, "visibility", emp51.employee_visibility)
    print("ma_bo_phan", emp51.ma_bo_phan_id.code if emp51.ma_bo_phan_id else None)
    print("legacy_mien", emp51._lug_employee_legacy_mien())
else:
    print("DOES NOT EXIST")

Mixin = env["hr.employee.access.mixin"]
print("\n=== ACCESS AS anh.trinh ===")
Pub = env["hr.employee.public"].with_user(u)
Emp = env["hr.employee"].with_user(u)
for eid in [51, u.employee_id.id if u.employee_id else None]:
    if not eid:
        continue
    e_pub = Pub.browse(eid)
    e_emp = Emp.browse(eid)
    print(f"\nemp {eid}:")
    print("  public exists", e_pub.exists(), "employee exists", e_emp.exists())
    try:
        e_pub.check_access("read")
        print("  public read OK")
    except Exception as ex:
        print("  public read FAIL", ex)
    try:
        e_emp.check_access("read")
        print("  employee read OK")
    except Exception as ex:
        print("  employee read FAIL", ex)
    if e_emp.exists():
        print("  edit_allowed", e_emp._lug_is_employee_profile_edit_allowed())
        try:
            e_emp.read(["name"])
            print("  read name OK", e_emp.name)
        except Exception as ex:
            print("  read name FAIL", type(ex).__name__, ex)

print("\n=== VP COUNTS ===")
for m in ["VP", "Nam", "Bắc", "ĐTT"]:
    tot = env["hr.employee"].sudo().search_count([("mien", "=", m)])
    vis_pub = Pub.search_count([("mien", "=", m)])
    vis_emp = Emp.search_count([("mien", "=", m)])
    print(f"  {m}: total={tot} public_visible={vis_pub} employee_visible={vis_emp}")

# What references employee 51 for user 85 on time off?
print("\n=== LEAVES referencing emp 51 ===")
Leave = env["hr.leave"].sudo()
leaves = Leave.search([("employee_id", "=", 51)], limit=5)
print("leave count", Leave.search_count([("employee_id", "=", 51)]))
for lv in leaves:
    try:
        lv_u = lv.with_user(u)
        lv_u.check_access("read")
        print("  leave", lv.id, "readable OK state", lv.state)
    except Exception as ex:
        print("  leave", lv.id, "readable FAIL", ex)

# User's own leave dashboard data
print("\n=== TIME OFF overview (hr.leave search as user) ===")
try:
    cnt = env["hr.leave"].with_user(u).search_count([])
    print("leave search_count", cnt)
except Exception as ex:
    print("FAIL", ex)

# Check if employee 51 is manager/coach ref
own = u.employee_id
if own:
    print("\n=== ORG REFS for own employee ===")
    print("parent", own.parent_id.id, own.parent_id.name if own.parent_id else None)
    print("coach", own.coach_id.id if own.coach_id else None)
