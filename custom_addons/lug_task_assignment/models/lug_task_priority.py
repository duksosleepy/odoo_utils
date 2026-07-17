# -*- coding: utf-8 -*-

from odoo import fields, models


class LugTaskPriority(models.Model):
    _name = "lug.task.priority"
    _description = "Mức độ ưu tiên / SLA"
    _order = "sequence, name"

    name = fields.Char(string="Mức độ", required=True, translate=True)
    code = fields.Char(string="Mã", required=True, index=True)
    sla_hours = fields.Float(
        string="SLA (giờ)",
        required=True,
        help="Thời gian phản hồi/hoàn thành tối đa tính từ khi giao việc.",
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint("unique(code)", "Mã mức độ phải là duy nhất.")
