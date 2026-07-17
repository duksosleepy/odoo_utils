# -*- coding: utf-8 -*-
u = env["res.users"].sudo().browse(85)
UserEmp = env["hr.employee"].with_user(u)
UserPub = env["hr.employee.public"].with_user(u)

for model, Rec in [("employee", UserEmp), ("public", UserPub)]:
    r = Rec.browse(44)
    try:
        print(model, "read", r.read(["name"]))
    except Exception as e:
        print(model, "read FAIL", type(e).__name__)

# direct super read on filtered public
allowed = UserPub.browse(44)._hr_employee_filter_accessible()
try:
    from odoo.addons.hr.models.hr_employee_public import HrEmployeePublic
except Exception:
    pass
try:
    data = super(type(UserPub), allowed).read(["name"])
    print("super public read", data)
except Exception as e:
    print("super public read FAIL", type(e).__name__, str(e)[:80].encode("unicode_escape").decode())
