# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import api, fields, SUPERUSER_ID

from odoo.addons.lug_security_audit.models.lug_hr_snapshot import job_title_label_from_employee


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    Session = env["lug.user.session"].sudo()
    Employee = env["hr.employee"]

    Session.action_backfill_job_titles()

    today = fields.Date.context_today(Session)
    for offset in range(31):
        day = today - timedelta(days=offset)
        Session._build_daily_summary_for_date(day)

    for session in Session.search([("employee_id", "!=", False), ("job_title_label", "=", False)]):
        employee = Employee.browse(session.employee_id.id)
        title = job_title_label_from_employee(employee)
        if title:
            session.write({"job_title_label": title})
