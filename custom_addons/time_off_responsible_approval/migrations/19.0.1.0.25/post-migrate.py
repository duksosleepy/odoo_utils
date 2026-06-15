import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    from odoo.addons.time_off_responsible_approval.hooks import (
        sync_hr_leave_visibility_rules,
    )

    sync_hr_leave_visibility_rules(env)
    _logger.info(
        "time_off_responsible_approval: applied hr.leave visibility security migration"
    )
