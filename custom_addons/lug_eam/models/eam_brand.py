# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EamBrand(models.Model):
    _name = "eam.brand"
    _description = "Thương hiệu tài sản"
    _order = "name"

    name = fields.Char(string="Thương hiệu", required=True, translate=True)
    code = fields.Char(
        string="Mã",
        index=True,
        copy=False,
        help="Để trống sẽ tự sinh theo chuẩn BR-0001.",
    )
    country_id = fields.Many2one("res.country", string="Xuất xứ")
    partner_id = fields.Many2one("res.partner", string="Hãng / Đại diện")
    logo = fields.Image(string="Logo", max_width=256, max_height=256)
    note = fields.Text(string="Ghi chú")
    model_ids = fields.One2many("eam.model", "brand_id", string="Model")
    model_count = fields.Integer(string="Số model", compute="_compute_model_count")
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint("unique(code)", "Mã thương hiệu phải là duy nhất.")
    _name_unique = models.Constraint("unique(name)", "Tên thương hiệu phải là duy nhất.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("code"):
                vals["code"] = self.env["ir.sequence"].next_by_code("eam.brand") or "/"
        return super().create(vals_list)

    def _compute_model_count(self):
        data = self.env["eam.model"]._read_group(
            [("brand_id", "in", self.ids)], ["brand_id"], ["__count"]
        )
        mapped = {brand.id: count for brand, count in data}
        for brand in self:
            brand.model_count = mapped.get(brand.id, 0)
