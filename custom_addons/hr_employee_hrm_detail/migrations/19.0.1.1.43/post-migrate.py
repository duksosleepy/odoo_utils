# -*- coding: utf-8 -*-

import logging

from odoo import SUPERUSER_ID, api

from odoo.addons.hr_employee_hrm_detail.hooks import _sync_mien_access_rules

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    obsolete = env.ref(
        "hr_employee_hrm_detail.access_hr_employee_hrm_staff",
        raise_if_not_found=False,
    )
    if obsolete:
        obsolete.unlink()
        _logger.info("Removed obsolete ACL access_hr_employee_hrm_staff")
    users = env["res.users"].search([])
    env.add_to_compute(env["res.users"]._fields["employee_ma_bo_phan_id"], users)
    env["res.users"].flush_model(["employee_ma_bo_phan_id"])
    _sync_mien_access_rules(env)
    env["hr.employee.public"].init()
    env.registry.clear_cache()
    _logger.info(
        "hr_employee_hrm_detail 1.1.43: staff uses hr.employee.public; synced store-scope rules"
    )
