# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID, api

from odoo.addons.hr_employee_hrm_detail.hooks import _sync_mien_access_rules


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _sync_mien_access_rules(env)
    env.add_to_compute(
        env["res.users"]._fields["hr_officer_mien_scope"],
        env["res.users"].search([]),
    )
    env["res.users"].flush_model(["hr_officer_mien_scope"])
    env.registry.clear_cache()
