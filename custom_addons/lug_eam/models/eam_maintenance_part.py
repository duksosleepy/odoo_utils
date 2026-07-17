# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EamMaintenancePart(models.Model):
    _name = "eam.maintenance.part"
    _description = "Linh kiện dùng trong phiếu bảo trì"

    request_id = fields.Many2one(
        "maintenance.request",
        required=True,
        ondelete="cascade",
        index=True,
    )
    product_id = fields.Many2one("product.product", string="Linh kiện", required=True)
    quantity = fields.Float(string="Số lượng", default=1.0, required=True)
    unit_cost = fields.Monetary(string="Đơn giá")
    currency_id = fields.Many2one(
        "res.currency",
        related="request_id.company_id.currency_id",
    )
    subtotal = fields.Monetary(
        string="Thành tiền",
        compute="_compute_subtotal",
        store=True,
    )

    @api.depends("quantity", "unit_cost")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = (line.quantity or 0.0) * (line.unit_cost or 0.0)
