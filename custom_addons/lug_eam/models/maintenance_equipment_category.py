# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class MaintenanceEquipmentCategory(models.Model):
    _inherit = "maintenance.equipment.category"
    _parent_name = "parent_id"
    _parent_store = True

    code = fields.Char(string="Mã danh mục", index=True)
    parent_id = fields.Many2one(
        "maintenance.equipment.category",
        string="Danh mục cha",
        index=True,
        ondelete="restrict",
    )
    parent_path = fields.Char(index=True, unaccent=False)
    complete_name = fields.Char(
        string="Tên đầy đủ", compute="_compute_complete_name", recursive=True, store=True
    )
    require_qr = fields.Boolean(string="Sinh QR", default=True)
    require_warranty = fields.Boolean(string="Bắt buộc bảo hành")
    maintenance_cycle_month = fields.Integer(
        string="Chu kỳ bảo trì (tháng)",
        help="Chu kỳ bảo trì phòng ngừa. 0 = không áp dụng.",
    )
    inspection_cycle_month = fields.Integer(
        string="Chu kỳ kiểm tra (tháng)",
        help="Chu kỳ kiểm tra/kiểm kê định kỳ. 0 = không áp dụng.",
    )

    _code_unique = models.Constraint(
        "unique(code)", "Mã danh mục tài sản phải là duy nhất."
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("code"):
                vals["code"] = self.env["ir.sequence"].next_by_code(
                    "eam.category"
                ) or "/"
        return super().create(vals_list)

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for cat in self:
            if cat.parent_id:
                cat.complete_name = f"{cat.parent_id.complete_name} / {cat.name}"
            else:
                cat.complete_name = cat.name

    @api.constrains("parent_id")
    def _check_category_recursion(self):
        if self._has_cycle():
            raise ValidationError(_("Không thể tạo danh mục cha lặp vòng."))
