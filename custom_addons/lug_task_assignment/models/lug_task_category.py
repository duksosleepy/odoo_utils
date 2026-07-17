# -*- coding: utf-8 -*-

from odoo import fields, models


class LugTaskCategory(models.Model):
    _name = "lug.task.category"
    _description = "Loại công việc IT"
    _order = "sequence, name"

    name = fields.Char(string="Tên loại việc", required=True, translate=True)
    code = fields.Char(string="Mã", required=True, index=True)
    point = fields.Float(
        string="Điểm mặc định",
        required=True,
        default=1.0,
        help="Điểm chấm công việc theo loại (Hỗ trợ=1, ERP=8, Dự án=10, ...).",
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint("unique(code)", "Mã loại việc phải là duy nhất.")
