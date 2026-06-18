# -*- coding: utf-8 -*-

from odoo import models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    def _check_access(self, operation):
        """Also hide assigned leave-approval activities outside Miền scope."""
        result = super()._check_access(operation)
        if operation != "read" or not self:
            return result

        leave_model = self.env["hr.leave"]
        if not leave_model._leave_mien_scope_restricts_user():
            return result

        leave_activities = self.sudo().filtered(
            lambda activity: activity.res_model == "hr.leave" and activity.res_id
        )
        if not leave_activities:
            return result

        allowed_ids = set(
            leave_model.search([("id", "in", leave_activities.mapped("res_id"))]).ids
        )
        forbidden = self.browse(
            [
                activity.id
                for activity in leave_activities
                if activity.res_id not in allowed_ids
            ]
        )
        if not forbidden:
            return result

        if result:
            return result[0] + forbidden, result[1]
        return forbidden, lambda: forbidden._make_access_error(operation)
