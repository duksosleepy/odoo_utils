# -*- coding: utf-8 -*-

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    eam_warehouse_ids = fields.Many2many(
        "stock.warehouse",
        "res_users_eam_warehouse_rel",
        "user_id",
        "warehouse_id",
        string="Kho EAM được phân công",
        help="Giới hạn phạm vi kho cho nhân viên kho (record rule).",
    )
