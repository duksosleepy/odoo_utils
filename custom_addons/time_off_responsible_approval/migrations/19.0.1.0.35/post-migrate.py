import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    pending = env["hr.leave"].sudo().search(
        [
            ("state", "in", ("confirm", "validate1")),
            ("validation_type", "in", ("employee_hr_responsibles", "multi_step_6")),
        ]
    )
    if pending:
        pending.activity_update()
    _logger.info(
        "time_off_responsible_approval: synced approval activities for %s pending leave(s)",
        len(pending),
    )
