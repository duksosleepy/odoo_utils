# -*- coding: utf-8 -*-

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # Các trường phục vụ in Phiếu xuất kho / Phiếu nhập mua theo mẫu Sáng Tâm
    eam_debit_account = fields.Char(string="Tài khoản Nợ")
    eam_credit_account = fields.Char(string="Tài khoản Có")
    eam_import_tax = fields.Float(string="Thuế nhập khẩu")
    eam_vat_amount = fields.Float(string="Thuế GTGT")

    def eam_num_vn(self, value, digits=0):
        """Định dạng số kiểu Việt Nam: ngăn nghìn bằng '.', thập phân bằng ','.

        Ví dụ: 18450000 -> '18.450.000'; 98980 với digits=2 -> '98.980,00'.
        """
        fmt = "{:,.%df}" % int(digits)
        text = fmt.format(value or 0.0)
        return text.replace(",", "X").replace(".", ",").replace("X", ".")
