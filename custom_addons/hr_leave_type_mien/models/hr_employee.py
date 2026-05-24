# -*- coding: utf-8 -*-

from odoo import models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _get_leave_mien(self):
        """Miền dùng để lọc loại ngày nghỉ (ưu tiên field Miền, sau đó Miền của mã bộ phận)."""
        self.ensure_one()
        if self.mien:
            return self.mien
        if self.ma_bo_phan_id and self.ma_bo_phan_id.mien:
            return self.ma_bo_phan_id.mien
        return False
