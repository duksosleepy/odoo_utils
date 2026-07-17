# -*- coding: utf-8 -*-

def post_init_hook(env):
    """Đăng ký ứng dụng LUG Permission nếu module đó đã cài."""
    if "lug.app" not in env:
        return
    App = env["lug.app"].sudo()
    if App.search([("code", "=", "lug_task_assignment")], limit=1):
        return
    App.create(
        {
            "name": "Giao việc IT",
            "code": "lug_task_assignment",
            "module_name": "lug_task_assignment",
            "sequence": 50,
            "active": True,
        }
    )
