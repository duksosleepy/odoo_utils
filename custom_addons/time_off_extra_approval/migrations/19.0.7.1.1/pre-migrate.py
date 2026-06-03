# -*- coding: utf-8 -*-

import logging

from odoo.tools import sql

_logger = logging.getLogger(__name__)

_DEFAULT_MAX_SKIP_JOB_TITLE = "trưởng bộ phận"


def migrate(cr, version):
    if not sql.table_exists(cr, "hr_leave_odoobot_notify_config"):
        return
    if sql.column_exists(cr, "hr_leave_odoobot_notify_config", "max_skip_job_title"):
        return
    if sql.column_exists(cr, "hr_leave_odoobot_notify_config", "max_stop_level"):
        _logger.info(
            "time_off_extra_approval: replace max_stop_level with max_skip_job_title"
        )
        cr.execute(
            """
            ALTER TABLE hr_leave_odoobot_notify_config
            DROP COLUMN max_stop_level
            """
        )
    cr.execute(
        f"""
        ALTER TABLE hr_leave_odoobot_notify_config
        ADD COLUMN max_skip_job_title VARCHAR
        DEFAULT '{_DEFAULT_MAX_SKIP_JOB_TITLE}'
        """
    )
    cr.execute(
        """
        UPDATE hr_leave_odoobot_notify_config
        SET max_skip_job_title = %s
        WHERE max_skip_job_title IS NULL
        """,
        (_DEFAULT_MAX_SKIP_JOB_TITLE,),
    )
