# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class ResUsers(models.Model):
    _inherit = "res.users"

    def write(self, vals):
        res = super().write(vals)
        if "group_ids" in vals:
            self.env.registry.clear_cache()
            bus = self.env["bus.bus"]
            for user in self:
                if user.partner_id:
                    bus._sendone(user.partner_id, "employee_privacy_refresh", {})
        return res
