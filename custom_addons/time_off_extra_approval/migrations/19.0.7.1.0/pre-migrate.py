# -*- coding: utf-8 -*-

import logging

from odoo.tools import sql

_logger = logging.getLogger(__name__)


def _column_exists(cr, table, column):
    return sql.column_exists(cr, table, column)


def migrate(cr, version):
    if not _column_exists(cr, "hr_leave", "approval_last_odoobot_remind_at"):
        _logger.info(
            "time_off_extra_approval: creating hr_leave.approval_last_odoobot_remind_at"
        )
        cr.execute(
            """
            ALTER TABLE hr_leave
            ADD COLUMN approval_last_odoobot_remind_at TIMESTAMP WITHOUT TIME ZONE
            """
        )
