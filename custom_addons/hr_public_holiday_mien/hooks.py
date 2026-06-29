# -*- coding: utf-8 -*-

from .public_holiday_seed import seed_public_holidays_if_empty


def post_init_hook(env):
    env["hr.employee"].search([])._sync_store_working_calendar()
    seed_public_holidays_if_empty(env)
