# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    from odoo import api

    env = api.Environment(cr, SUPERUSER_ID, {})
    manager = env.ref("lug_security_audit.group_lug_security_manager", raise_if_not_found=False)
    system = env.ref("base.group_system", raise_if_not_found=False)
    if not manager or not system:
        return
    users = system.user_ids.filtered(lambda user: user.active)
    if users:
        manager.sudo().write({"user_ids": [(4, user.id) for user in users]})
