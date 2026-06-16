# Rebuild hr_employee_public SQL view with monthly leave bonus tracking columns.


def migrate(cr, version):
    from odoo import SUPERUSER_ID, api

    env = api.Environment(cr, SUPERUSER_ID, {})
    env["hr.employee.public"].init()
