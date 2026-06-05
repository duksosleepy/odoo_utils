# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.hr_employee_hrm_detail.hooks import _sync_mien_access_rules

    _sync_mien_access_rules(env)
    env.registry.clear_cache()
    _logger.info("hr_employee_hrm_detail: fixed flat Miền officer ir.rule domains")
