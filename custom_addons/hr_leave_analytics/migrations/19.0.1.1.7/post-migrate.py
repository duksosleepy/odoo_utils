from odoo import api, SUPERUSER_ID

from odoo.addons.hr_leave_analytics.hooks import _invalidate_web_assets


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    _invalidate_web_assets(env)
