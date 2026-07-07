# -*- coding: utf-8 -*-

def post_init_hook(env):
    _sync_lug_email_user_scopes(env)


def _sync_lug_email_user_scopes(env):
    admin_group = env.ref(
        "lug_email_account.group_lug_email_admin",
        raise_if_not_found=False,
    )
    if admin_group:
        admin_group.all_user_ids._sync_lug_email_scope_from_access()
    access_users = env["lug.email.access"].search([]).mapped("user_id")
    if access_users:
        access_users._sync_lug_email_scope_from_access()
