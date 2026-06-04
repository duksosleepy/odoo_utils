# -*- coding: utf-8 -*-

from odoo import models


class DiscussChannelMember(models.Model):
    _inherit = "discuss.channel.member"

    def _to_store_persona(self, fields=None):
        mixin = self.env["hr.employee.access.mixin"]
        if mixin._hr_employee_discuss_access_applies() and fields is None:
            fields = "avatar_card"
        return super()._to_store_persona(fields)
