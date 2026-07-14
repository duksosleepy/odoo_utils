# -*- coding: utf-8 -*-

from odoo import fields, models


class HrKho(models.Model):
    _name = 'hr.kho'
    _description = 'Mã Kho'
    _order = 'code, name'
    _rec_name = 'code'

    name = fields.Char(string='Tên kho', required=True, translate=True)
    code = fields.Char(string='Mã kho', required=True, help='Mã nội bộ, ví dụ: KHO-HN')
    mien = fields.Selection(
        selection=[
            ('Bắc', 'Bắc'),
            ('Nam', 'Nam'),
            ('ĐTT', 'ĐTT'),
            ('VP', 'VP'),
        ],
        string='Miền',
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )
    note = fields.Text(string='Ghi chú')

    _code_company_unique = models.Constraint(
        'unique(code, company_id)',
        'Mã kho phải là duy nhất trong cùng công ty.',
    )
