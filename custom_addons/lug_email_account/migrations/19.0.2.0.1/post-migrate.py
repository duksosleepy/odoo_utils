# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.lug_email_account.hooks import _sync_lug_email_user_scopes

    _sync_lug_email_user_scopes(env)
