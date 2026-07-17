# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    eam_is_maintenance_provider = fields.Boolean(
        string="Đơn vị bảo trì",
        help="Đánh dấu nhà cung cấp / đơn vị thực hiện bảo trì tài sản.",
    )
