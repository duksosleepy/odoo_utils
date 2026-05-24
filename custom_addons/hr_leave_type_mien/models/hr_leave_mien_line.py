# -*- coding: utf-8 -*-

from odoo import fields, models


class HrLeaveMienLine(models.Model):
    _name = "hr.leave.mien.line"
    _description = "Dòng loại ngày nghỉ theo Miền"
    _order = "sequence, id"

    config_id = fields.Many2one(
        "hr.leave.mien.config",
        required=True,
        ondelete="cascade",
        index=True,
    )
    leave_type_id = fields.Many2one(
        "hr.leave.type",
        string="Loại ngày nghỉ",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(default=10)

    _leave_type_unique = models.Constraint(
        "unique (config_id, leave_type_id)",
        "Mỗi loại ngày nghỉ chỉ được gán một lần cho cùng một Miền.",
    )
