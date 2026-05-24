# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

from odoo.addons.hr_holidays.models.hr_leave import get_employee_from_context


class HrLeave(models.Model):
    _inherit = "hr.leave"

    mien_allowed_leave_type_ids = fields.Many2many(
        comodel_name="hr.leave.type",
        relation="hr_leave_mien_allowed_leave_type_rel",
        column1="leave_id",
        column2="leave_type_id",
        string="Loại phép theo Miền",
        compute="_compute_mien_allowed_leave_type_ids",
        store=True,
        readonly=True,
    )

    @api.depends("employee_id", "employee_id.mien", "employee_id.ma_bo_phan_id.mien")
    def _compute_mien_allowed_leave_type_ids(self):
        LeaveType = self.env["hr.leave.type"]
        for leave in self:
            employee = leave.employee_id
            if not employee:
                leave.mien_allowed_leave_type_ids = False
                continue
            domain = leave._leave_type_domain_for_employee(employee)
            leave.mien_allowed_leave_type_ids = LeaveType.with_context(
                employee_id=employee.id
            ).search(domain)

    def onchange(self, values, field_names, fields_spec):
        """Đảm bảo RPC loại phép nhận employee_id (client không gửi default_*)."""
        if values and "employee_id" in fields_spec:
            employee_id = get_employee_from_context(
                values, self.env.context, self.env.user.employee_id.id
            )
            if employee_id:
                self = self.with_context(
                    employee_id=employee_id,
                    default_employee_id=employee_id,
                )
        return super().onchange(values, field_names, fields_spec)

    @api.model
    def _leave_type_base_domain(self):
        return [
            "|",
            ("requires_allocation", "=", False),
            "&",
            ("has_valid_allocation", "=", True),
            "|",
            ("allows_negative", "=", True),
            "&",
            ("virtual_remaining_leaves", ">", 0),
            ("allows_negative", "=", False),
        ]

    @api.model
    def _leave_type_domain_for_employee(self, employee):
        domain = list(self._leave_type_base_domain())
        if not employee:
            return domain
        mien = employee._get_leave_mien()
        if not mien:
            return domain
        MienConfig = self.env["hr.leave.mien.config"]
        if not MienConfig._is_mien_configured(mien):
            return domain
        allowed_ids = MienConfig._get_leave_type_ids_for_mien(mien)
        domain = ["&"] + domain + [("id", "in", allowed_ids or [0])]
        return domain

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if not self.env.context.get("holiday_status_display_name", True) or "holiday_status_id" not in fields_list:
            return res
        employee = (
            self.env["hr.employee"].browse(res["employee_id"])
            if res.get("employee_id")
            else self.env.user.employee_id
        )
        domain = self._leave_type_domain_for_employee(employee)
        leave_types = self.env["hr.leave.type"].search(domain, order="sequence")
        selected = next(
            (
                leave_type
                for leave_type in leave_types
                if (res.get("request_unit_hours") and leave_type.request_unit == "hour")
                or (not res.get("request_unit_hours"))
            ),
            leave_types[:1],
        )
        if selected:
            res["holiday_status_id"] = selected.id
            res["request_unit_hours"] = selected.request_unit == "hour"
        else:
            res["holiday_status_id"] = False
        return res

    @api.onchange("employee_id")
    def _onchange_employee_id_mien_leave_type(self):
        employee = self.employee_id
        if not employee:
            return {}
        domain = self._leave_type_domain_for_employee(employee)
        allowed_ids = (
            self.env["hr.leave.type"]
            .with_context(employee_id=employee.id)
            .search(domain)
            .ids
        )
        mien = employee._get_leave_mien()
        if (
            self.holiday_status_id
            and mien
            and self.env["hr.leave.mien.config"]._is_mien_configured(mien)
            and self.holiday_status_id.id not in allowed_ids
        ):
            self.holiday_status_id = False
        return {"domain": {"holiday_status_id": [("id", "in", allowed_ids)]}}

    @api.constrains("employee_id", "holiday_status_id")
    def _check_holiday_status_mien(self):
        MienConfig = self.env["hr.leave.mien.config"]
        for leave in self:
            if not leave.employee_id or not leave.holiday_status_id:
                continue
            mien = leave.employee_id._get_leave_mien()
            if not mien:
                continue
            if not MienConfig._is_mien_configured(mien):
                continue
            allowed_ids = MienConfig._get_leave_type_ids_for_mien(mien)
            if leave.holiday_status_id.id not in allowed_ids:
                raise ValidationError(
                    _("Loại ngày nghỉ «%s» không áp dụng cho Miền %s của nhân viên.")
                    % (leave.holiday_status_id.name, mien)
                )
