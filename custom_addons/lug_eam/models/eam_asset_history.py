# -*- coding: utf-8 -*-

from odoo import fields, models


class EamAssetHistory(models.Model):
    _name = "eam.asset.history"
    _description = "Lịch sử tài sản"
    _order = "change_date desc, id desc"

    asset_id = fields.Many2one(
        "maintenance.equipment",
        string="Tài sản",
        required=True,
        ondelete="cascade",
        index=True,
    )
    asset_code = fields.Char(
        string="Mã tài sản", related="asset_id.asset_code", store=True
    )
    change_date = fields.Datetime(
        string="Thời điểm", default=fields.Datetime.now, index=True
    )
    user_id = fields.Many2one(
        "res.users", string="Người thực hiện", default=lambda self: self.env.user
    )
    event_type = fields.Selection(
        [
            ("create", "Tạo mới"),
            ("state", "Đổi trạng thái"),
            ("location", "Đổi vị trí"),
            ("owner", "Đổi người giữ"),
            ("transaction", "Giao dịch"),
        ],
        string="Loại thay đổi",
        required=True,
        index=True,
    )
    old_value = fields.Char(string="Giá trị cũ")
    new_value = fields.Char(string="Giá trị mới")
    note = fields.Char(string="Diễn giải")
