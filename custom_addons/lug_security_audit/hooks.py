# -*- coding: utf-8 -*-


def post_init_hook(env):
    """Grant Lug Security to all Settings administrators."""
    manager = env.ref("lug_security_audit.group_lug_security_manager", raise_if_not_found=False)
    system = env.ref("base.group_system", raise_if_not_found=False)
    if not manager or not system:
        return
    users = system.user_ids.filtered(lambda user: user.active)
    if users:
        manager.sudo().write({"user_ids": [(4, user.id) for user in users]})
