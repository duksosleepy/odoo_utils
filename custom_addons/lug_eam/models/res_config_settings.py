# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    eam_warranty_alert_days = fields.Integer(
        string="Cảnh báo bảo hành (ngày)",
        default=30,
        config_parameter="lug_eam.warranty_alert_days",
    )
    eam_maintenance_approval_amount = fields.Float(
        string="Ngưỡng duyệt chi phí BT",
        default=5000000,
        config_parameter="lug_eam.maintenance_approval_amount",
    )
    eam_sla_hours = fields.Integer(
        string="SLA xử lý BT (giờ)",
        default=48,
        config_parameter="lug_eam.sla_hours",
    )
