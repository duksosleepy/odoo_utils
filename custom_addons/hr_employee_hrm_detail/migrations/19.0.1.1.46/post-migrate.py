# Rebuild hr_employee_public SQL view with time-off balance columns.

def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    env["hr.employee.public"].init()
