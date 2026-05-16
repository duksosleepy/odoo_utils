# -*- coding: utf-8 -*-
"""Khi module được nâng cấp về trạng thái installed, chạy bulk inject (post_init không chạy lúc upgrade)."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    def write(self, vals):
        res = super().write(vals)
        if vals.get("state") != "installed":
            return res
        if not self.filtered(lambda m: m.name == "mail_discuss_mobile_links"):
            return res
        try:
            self.env["mail.message"]._mdl_bulk_inject()
        except Exception:
            _logger.exception("mail_discuss_mobile_links: bulk inject after module install/upgrade failed")
        return res
