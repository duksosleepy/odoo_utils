# -*- coding: utf-8 -*-

from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        result = super().session_info()
        result["lug_security_audit"] = {
            "enabled": bool(self.env.user and not self.env.user._is_public()),
            "heartbeat_interval_ms": 30000,
        }
        return result
