# -*- coding: utf-8 -*-

import odoo
from odoo import SUPERUSER_ID

odoo.tools.config.parse_config(["-c", r"d:\Lap_odoo\odoo.conf"])
registry = odoo.registry("lap_odoo19")
with registry.cursor() as cr:
    env = odoo.api.Environment(cr, SUPERUSER_ID, {})
    Session = env["lug.user.session"]
    user = env["res.users"].search([("login", "=", "admin")], limit=1)
    if not user:
        user = env["res.users"].search([("active", "=", True)], limit=1)
    snapshot = Session._employee_org_snapshot(user)
    print("user:", user.login, "snapshot:", snapshot)
    cr.rollback()
