# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

channel = env.ref("mail.menu_channel")
config = env.ref("mail.menu_configuration")
Menu = env["ir.ui.menu"]

def check(label, user):
    hidden = set(Menu.with_user(user)._load_menus_blacklist())
    print(f"{label}: Kenh hidden={channel.id in hidden}, Cau hinh hidden={config.id in hidden}")

check("Administrator", env["res.users"].browse(2))
check("phu.chau", env["res.users"].sudo().search([("login", "=", "phu.chau@sangtam.com")], limit=1))
check("anh.trinh", env["res.users"].browse(85))
