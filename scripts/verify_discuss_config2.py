# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

config_menu = env.ref("mail.menu_configuration")
Menu = env["ir.ui.menu"]

def check(label, user):
    hidden = config_menu.id in set(Menu.with_user(user)._load_menus_blacklist())
    print(f"{label}: Cau hinh hidden={hidden} lug={user._lug_permission_is_enforced()} admin={user.has_group('base.group_system')}")

# find phuong user
for term in ["Phuong", "phuong", "phu.chau"]:
    users = env["res.users"].sudo().search(["|", ("login", "ilike", term), ("name", "ilike", term)], limit=3)
    for u in users:
        check(u.login, u)

# random internal user without lug
plain = env["res.users"].sudo().search([
    ("share", "=", False),
    ("lug_group_ids", "=", False),
    ("id", "not in", [1, 2]),
], limit=3)
for u in plain:
    check(f"plain {u.login}", u)
