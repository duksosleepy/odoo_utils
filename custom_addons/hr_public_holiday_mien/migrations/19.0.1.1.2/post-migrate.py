# -*- coding: utf-8 -*-

from odoo.addons.hr_public_holiday_mien.public_holiday_seed import seed_public_holidays_if_empty


def migrate(cr, version):
    from odoo import api

    env = api.Environment(cr, 1, {})
    seed_public_holidays_if_empty(env)
