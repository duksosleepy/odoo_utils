# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EamModel(models.Model):
    _name = "eam.model"
    _description = "Model / Chủng loại tài sản"
    _order = "name"

    name = fields.Char(string="Model", required=True, translate=True)
    code = fields.Char(
        string="Mã",
        index=True,
        copy=False,
        help="Để trống sẽ tự sinh theo chuẩn MD-00001.",
    )
    category_id = fields.Many2one(
        "maintenance.equipment.category",
        string="Nhóm tài sản",
        required=True,
        index=True,
    )
    brand_id = fields.Many2one("eam.brand", string="Thương hiệu", required=True, index=True)
    specification = fields.Text(string="Thông số kỹ thuật")
    default_warranty_month = fields.Integer(string="Bảo hành mặc định (tháng)")
    default_cost = fields.Monetary(string="Giá tham chiếu", currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency",
        string="Tiền tệ",
        default=lambda self: self.env.company.currency_id,
    )
    image = fields.Image(string="Hình ảnh", max_width=1024, max_height=1024)
    equipment_ids = fields.One2many(
        "maintenance.equipment", "eam_model_id", string="Tài sản"
    )
    equipment_count = fields.Integer(
        string="Số tài sản", compute="_compute_equipment_count"
    )
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint("unique(code)", "Mã model phải là duy nhất.")
    _cat_brand_name_unique = models.Constraint(
        "unique(category_id, brand_id, name)",
        "Model đã tồn tại trong cùng nhóm tài sản và thương hiệu.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("code"):
                vals["code"] = self.env["ir.sequence"].next_by_code("eam.model") or "/"
        return super().create(vals_list)

    @api.depends("name", "brand_id.name", "category_id.name")
    def _compute_display_name(self):
        for rec in self:
            parts = []
            if rec.category_id:
                parts.append(rec.category_id.name)
            if rec.brand_id:
                parts.append(rec.brand_id.name)
            label = " / ".join(parts)
            rec.display_name = f"{label} {rec.name}".strip() if label else (rec.name or "")

    def _compute_equipment_count(self):
        data = self.env["maintenance.equipment"]._read_group(
            [("eam_model_id", "in", self.ids)], ["eam_model_id"], ["__count"]
        )
        mapped = {model.id: count for model, count in data}
        for rec in self:
            rec.equipment_count = mapped.get(rec.id, 0)
