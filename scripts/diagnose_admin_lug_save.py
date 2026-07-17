# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u = env["res.users"].sudo().browse(58)
own = u.employee_id
print("own emp", own.id, own.name, "mien", own.mien, "zone", own.mien_zone_id.legacy_mien if own.mien_zone_id else None)
print("employee_mien field", u.employee_mien)

# All mien values in DB
env.cr.execute("SELECT mien, count(*) FROM hr_employee e JOIN hr_version v ON v.id = e.current_version_id GROUP BY mien ORDER BY 2 DESC")
print("mien distribution", env.cr.fetchall()[:15])

# Employees admin.lug can see
UserPub = env["hr.employee.public"].with_user(u)
for e in UserPub.search([]):
    print("visible", e.id, e.name, "mien", e.mien)

# Employees in Nam that should be editable
Emp = env["hr.employee"].with_user(u)
nam_all = env["hr.employee"].sudo().search([("mien", "=", "Nam")])
print("Nam total sudo", len(nam_all))
nam_vis = Emp.search([("mien", "=", "Nam")])
print("Nam visible", nam_vis.ids)

# Test save path on emp 33
e33 = Emp.browse(33)
print("e33 mien", e33.mien, "parent", e33.parent_id.id, e33.parent_id.name if e33.parent_id else None)
UserPub.browse(33)._hr_employee_read_is_restricted()
try:
    e33.web_read({"name": {}, "parent_id": {"fields": {"display_name": {}}}})
    print("web_read 33 OK")
except Exception as ex:
    print("web_read 33 FAIL", str(ex)[:200])

# parent 81 (VP) - admin.lug's manager?
try:
    UserPub.browse(81).check_access("read")
    print("read 81 OK")
except Exception as ex:
    print("read 81 FAIL", str(ex)[:150])

# Simulate write
try:
    e33.with_context(skip_lug_employee_profile_edit_check=True).write({"work_phone": e33.work_phone or "test"})
    print("write 33 OK")
except Exception as ex:
    print("write 33 FAIL", str(ex)[:200])

# After write web_read
try:
    e33.web_read({"display_name": {}, "parent_id": {"fields": {"display_name": {}}}})
    print("post-write web_read OK")
except Exception as ex:
    print("post-write web_read FAIL", str(ex)[:200])
