# -*- coding: utf-8 -*-
u = env["res.users"].browse(85)
e81 = env["hr.employee"].sudo().browse(81)
e44 = env["hr.employee"].sudo().browse(44)
print("e81", e81.name, "parent_id", e81.parent_id.id, e81.parent_id.name)
print("e81 version parent", e81.current_version_id.parent_id.id if e81.current_version_id else None)
print("e44", e44.name, "active", e44.active, "dept", e44.department_id.id, "mien", e44.mien)
pub81 = env["hr.employee.public"].with_user(u).browse(81)
try:
    d = pub81.read(["name", "parent_id"])
    print("read 81", d)
except Exception as ex:
    print("read 81 fail", ex)
try:
    d = pub81.web_read({"name": {}, "parent_id": {"fields": {"display_name": {}}}})
    print("web_read 81", d)
except Exception as ex:
    print("web_read 81 fail", ex)
