# -*- coding: utf-8 -*-

from odoo.addons.hr_employee_hrm_detail.hooks import _sync_mien_access_rules


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    _sync_mien_access_rules(env)
