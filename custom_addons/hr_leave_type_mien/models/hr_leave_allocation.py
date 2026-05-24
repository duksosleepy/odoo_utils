# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class HrLeaveAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    @api.onchange("employee_id")
    def _onchange_employee_id_mien_leave_type(self):
        employee = self.employee_id
        domain = self.env["hr.leave"]._leave_type_domain_for_employee(employee)
        MienConfig = self.env["hr.leave.mien.config"]
        mien = employee._get_leave_mien() if employee else False
        if (
            employee
            and self.holiday_status_id
            and mien
            and MienConfig._is_mien_configured(mien)
        ):
            allowed_ids = MienConfig._get_leave_type_ids_for_mien(mien)
            if self.holiday_status_id.id not in allowed_ids:
                self.holiday_status_id = False
        return {"domain": {"holiday_status_id": domain}}

    @api.constrains("employee_id", "holiday_status_id")
    def _check_holiday_status_mien(self):
        MienConfig = self.env["hr.leave.mien.config"]
        for allocation in self:
            if not allocation.employee_id or not allocation.holiday_status_id:
                continue
            mien = allocation.employee_id._get_leave_mien()
            if not mien:
                continue
            if not MienConfig._is_mien_configured(mien):
                continue
            allowed_ids = MienConfig._get_leave_type_ids_for_mien(mien)
            if allocation.holiday_status_id.id not in allowed_ids:
                raise ValidationError(
                    _("Loại ngày nghỉ «%s» không áp dụng cho Miền %s của nhân viên.")
                    % (allocation.holiday_status_id.name, mien)
                )
