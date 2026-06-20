# -*- coding: utf-8 -*-

def post_init_hook(env):
    users = env["res.users"].search([]).filtered(
        lambda user: user._lug_permission_is_enforced()
    )
    if users:
        users._sync_lug_odoo_groups()
        env["res.users"]._lug_clear_menu_cache_global(env)
