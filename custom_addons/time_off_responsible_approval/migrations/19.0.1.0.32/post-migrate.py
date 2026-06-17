import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

_OFFICER_READ_DOMAIN = "[(1, '=', 1)]"
_OFFICER_UPDATE_DOMAIN = """[
    '|',
        '&',
            ('employee_id.user_id', '=', user.id),
            ('state', '!=', 'validate'),
        '|',
            ('employee_id.user_id', '!=', user.id),
            ('employee_id.user_id', '=', False)
]"""


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.time_off_responsible_approval.hooks import (
        sync_hr_leave_visibility_rules,
    )

    restored = env["ir.rule"]
    for xmlid, domain in (
        ("hr_holidays.hr_leave_rule_user_read", _OFFICER_READ_DOMAIN),
        ("hr_holidays.hr_leave_rule_officer_update", _OFFICER_UPDATE_DOMAIN),
    ):
        rule = env.ref(xmlid, raise_if_not_found=False)
        if rule and rule.domain_force != domain:
            rule.sudo().write({"domain_force": domain})
            restored |= rule
    sync_hr_leave_visibility_rules(env)
    env.registry.clear_cache()
    _logger.info(
        "time_off_responsible_approval: restored officer hr.leave rules %s",
        restored.ids,
    )
