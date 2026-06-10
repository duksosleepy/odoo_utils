import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    from odoo import SUPERUSER_ID, api

    env = api.Environment(cr, SUPERUSER_ID, {})
    pending = env["hr.leave"].search(
        [
            ("state", "in", ("confirm", "validate1")),
            ("validation_type", "=", "employee_hr_responsibles"),
        ]
    )
    if not pending:
        return
    pending._ensure_responsible_approval_lines()
    pending._compute_approval_actionable_user_ids()
    pending.flush_recordset(["approval_actionable_user_ids"])
    _logger.info(
        "time_off_responsible_approval: refreshed actionable users for %s pending leave(s)",
        len(pending),
    )
