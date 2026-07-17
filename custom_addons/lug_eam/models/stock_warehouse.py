# -*- coding: utf-8 -*-

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    # Bỏ giới hạn 5 ký tự mặc định của Odoo cho "Tên viết tắt" (mã kho)
    # size=0 => varchar không giới hạn (size phải là số nguyên, không dùng False)
    code = fields.Char(size=0)
