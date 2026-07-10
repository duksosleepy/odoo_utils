# -*- coding: utf-8 -*-

import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

POSITION_LABEL_MAP = {
    "director": "Giám đốc",
    "deputy_director": "Phó Giám đốc",
    "dept_head": "Trưởng phòng",
    "deputy_head": "Phó phòng",
    "team_lead": "Trưởng nhóm",
    "staff": "Nhân viên",
    "warehouse_keeper": "Thủ kho",
    "accountant": "Kế toán",
    "hr": "HCNS",
    "marketing": "Marketing",
    "it": "IT",
    "other": "Khác",
}


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    Account = env["lug.email.account"]
    Job = env["hr.job"]

    cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'lug_email_account'
          AND column_name = 'position'
    """)
    has_position = bool(cr.fetchone())

    for account in Account.search([]):
        vals = {}
        if not account.job_id:
            job = False
            if account.employee_id and account.employee_id.job_id:
                job = account.employee_id.job_id
            elif has_position:
                cr.execute(
                    "SELECT position FROM lug_email_account WHERE id = %s",
                    (account.id,),
                )
                row = cr.fetchone()
                if row and row[0]:
                    label = POSITION_LABEL_MAP.get(row[0], row[0])
                    job = Job.search([("name", "=ilike", label)], limit=1)
            if job:
                vals["job_id"] = job.id

        if not (account.phone or "").strip() and account.employee_id:
            phone = account.employee_id.mobile_phone or account.employee_id.work_phone
            if phone:
                vals["phone"] = phone

        if vals:
            account.write(vals)

    _logger.info("Migrated lug.email.account job_id and phone from HR data")
