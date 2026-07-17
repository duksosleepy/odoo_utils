# -*- coding: utf-8 -*-

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    eam_loc_kind = fields.Selection(
        [
            ("warehouse", "Kho"),
            ("zone", "Khu (Zone)"),
            ("rack", "Kệ (Rack)"),
            ("shelf", "Tầng kệ (Shelf)"),
            ("bin", "Ô (Bin)"),
            ("site", "Địa điểm (Site)"),
            ("building", "Tòa nhà"),
            ("floor", "Tầng"),
            ("room", "Phòng"),
            ("machine", "Vị trí máy"),
        ],
        string="Loại vị trí EAM",
    )
    eam_code = fields.Char(string="Mã vị trí", index=True)
    eam_department_id = fields.Many2one(
        "hr.department", string="Phòng ban sử dụng"
    )

    def _eam_is_warehouse_kind(self):
        self.ensure_one()
        return self.eam_loc_kind in ("warehouse", "zone", "rack", "shelf", "bin")

    def _eam_is_usage_kind(self):
        self.ensure_one()
        return self.eam_loc_kind in ("site", "building", "floor", "room", "machine")
