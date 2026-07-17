# -*- coding: utf-8 -*-
u = env["res.users"].sudo().search([("login", "=", "anh.trinh@sangtam.com")], limit=1)
UserEnv = env["res.users"].with_user(u)
try:
    data = UserEnv.browse(u.id).read(["name", "login", "email"])
    print("basic read OK")
except Exception as e:
    print("basic read FAIL", type(e).__name__)

from odoo.addons.hr_employee_self_only.models.hr_employee_privacy import (
    _privacy_can_edit_employee_profile,
    _privacy_is_employee_edit_forbidden,
)
print("privacy can edit", _privacy_can_edit_employee_profile(env["res.users"].with_user(u).env))
print("privacy forbidden", _privacy_is_employee_edit_forbidden(env["res.users"].with_user(u).env))
