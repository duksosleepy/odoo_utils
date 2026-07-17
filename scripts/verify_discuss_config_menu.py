# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

config_menu = env.ref("mail.menu_configuration")
Menu = env["ir.ui.menu"]

def check_user(label, user):
    hidden = set(Menu.with_user(user)._load_menus_blacklist())
    visible = config_menu.id not in hidden
    discuss_perms = user._lug_effective_permission_map().get("discuss", set()) if user._lug_permission_is_enforced() else set()
    print(f"{label} (id={user.id})")
    print(f"  lug_enforced={user._lug_permission_is_enforced()} discuss_perms={discuss_perms or '-'}")
    print(f"  is_admin={user.has_group('base.group_system')}")
    print(f"  Cấu hình visible={visible}")

# Regular employee from screenshot
u = env["res.users"].sudo().search([("name", "ilike", "Nguyễn Thị Phương")], limit=1)
if u:
    check_user("Nguyen Thi Phuong", u)
else:
    print("Nguyen Thi Phuong not found")

check_user("anh.trinh", env["res.users"].browse(85))
check_user("Administrator", env["res.users"].browse(2))

# User with discuss edit (if any)
for u in env["res.users"].sudo().search([("lug_group_ids", "!=", False)]):
    perms = u._lug_effective_permission_map().get("discuss", set())
    if perms - {"view"}:
        check_user(f"has discuss edit: {u.login}", u)
        break
