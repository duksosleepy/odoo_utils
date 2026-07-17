# -*- coding: utf-8 -*-
User = env["res.users"].sudo()
Emp = env["hr.employee"].sudo()
Pub = env["hr.employee.public"].sudo()

u = User.browse(85)
print("user", u.id, u.login.encode("unicode_escape").decode(), u.name.encode("unicode_escape").decode())
print("visibility", u.visibility_policy, "lug_scope", u.lug_data_scope, "mien", u.employee_mien)
print("lug_enforced", u._lug_permission_is_enforced())

for model, rec_id in [("hr.employee", 44), ("hr.employee.public", 44)]:
    rec = env[model].sudo().browse(rec_id)
    print(model, "exists", rec.exists(), "active", rec.active if rec.exists() else None)
    if rec.exists():
        print("  name", rec.name.encode("unicode_escape").decode(), "mien", repr(getattr(rec, "mien", None)))

emp44 = Emp.browse(44)
pub44 = Pub.browse(44)
print("public has employee_id", hasattr(pub44, "employee_id"))
if emp44.exists():
    print("emp44 department", emp44.department_id.id, pub44.department_id.id if pub44.exists() else None)

UserEnv = env["hr.employee"].with_user(u)
UserPub = env["hr.employee.public"].with_user(u)
try:
    r = UserEnv.browse(44)
    print("employee read exists", r.exists(), "name", r.name.encode("unicode_escape").decode() if r.exists() else None)
except Exception as e:
    print("employee FAIL", type(e).__name__)

try:
    r = UserPub.browse(44)
    print("public read exists", r.exists())
    if r.exists():
        print("  name", r.name.encode("unicode_escape").decode())
except Exception as e:
    print("public FAIL", type(e).__name__, str(e)[:100].encode("unicode_escape").decode())

try:
    r = UserPub.browse(44)
    data = r.read(["name"])
    print("public read() OK", data)
except Exception as e:
    print("public read() FAIL", type(e).__name__, str(e)[:120].encode("unicode_escape").decode())
