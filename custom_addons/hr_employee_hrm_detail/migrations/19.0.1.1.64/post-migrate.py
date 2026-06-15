# -*- coding: utf-8 -*-
"""Deduct retroactive previous-year requests created after the annual snapshot."""

import logging
from datetime import date

from odoo import SUPERUSER_ID, api, fields

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    today = fields.Date.context_today(env["hr.leave"])
    current_year_start = date(today.year, 1, 1)
    previous_year_start = date(today.year - 1, 1, 1)
    previous_year_end = date(today.year - 1, 12, 31)
    leaves = env["hr.leave"].search(
        [
            ("create_date", ">=", current_year_start),
            ("request_date_from", ">=", previous_year_start),
            ("request_date_from", "<=", previous_year_end),
            ("state", "in", ("confirm", "validate1", "validate")),
            ("previous_year_balance_deduction", "=", 0),
        ]
    )
    registered = leaves._register_previous_year_balance_leaves()
    leaves._rebalance_previous_year_balance(
        registered.mapped("employee_id").ids
    )
    _logger.info(
        "hr_employee_hrm_detail: checked %d retroactive previous-year requests",
        len(leaves),
    )
