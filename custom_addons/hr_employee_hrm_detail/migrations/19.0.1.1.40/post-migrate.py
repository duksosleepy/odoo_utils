# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)

_LEAVE_MANAGER_DOMAIN = """['|', '|', '|', '|',
    ('company_id', 'in', company_ids + [False]),
    ('parent_id.user_id', '=', user.id),
    ('id', '=', user.employee_id.parent_id.id),
    ('user_id', '=', user.id),
    ('leave_manager_id', '=', user.id)
]"""


def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    for xmlid in ("hr.hr_employee_comp_rule", "hr.hr_employee_public_comp_rule"):
        rule = env.ref(xmlid, raise_if_not_found=False)
        if not rule:
            _logger.warning("hr_employee_hrm_detail: missing ir.rule %s", xmlid)
            continue
        rule.write({"domain_force": _LEAVE_MANAGER_DOMAIN})
    _logger.info(
        "hr_employee_hrm_detail: extended employee record rules with leave_manager_id"
    )
