# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.fields import Domain

from .hr_leave_mien_config import MIEN_SELECTION

# Chỉ lọc loại phép theo Miền khi tạo đơn nghỉ (holiday_status_id trên hr.leave).
MIEN_LEAVE_TYPE_FILTER_CTX = "filter_leave_types_by_employee_mien"
MIEN_LEAVE_TYPE_SKIP_CTX = "skip_mien_leave_type_filter"


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    mien_line_ids = fields.One2many(
        "hr.leave.mien.line",
        "leave_type_id",
        string="Phân chia Miền",
    )
    mien_display = fields.Char(
        compute="_compute_mien_display",
        string="Miền",
    )

    @api.depends("mien_line_ids", "mien_line_ids.config_id.mien")
    def _compute_mien_display(self):
        labels = dict(MIEN_SELECTION)
        for leave_type in self:
            codes = leave_type.mien_line_ids.config_id.mapped("mien")
            leave_type.mien_display = ", ".join(labels.get(code, code) for code in codes) if codes else ""

    @api.model
    def _get_employee_id_for_mien_filter(self):
        ctx = self.env.context
        for key in ("employee_id", "default_employee_id"):
            employee_id = ctx.get(key)
            if not employee_id:
                continue
            if isinstance(employee_id, int):
                return employee_id
            if isinstance(employee_id, (list, tuple)):
                return employee_id[0]
            return employee_id
        if ctx.get("active_model") == "hr.leave" and ctx.get("active_id"):
            leave = self.env["hr.leave"].browse(ctx["active_id"])
            if leave.employee_id:
                return leave.employee_id.id
        return False

    @api.model
    def _should_apply_mien_leave_type_filter(self):
        ctx = self.env.context
        if ctx.get(MIEN_LEAVE_TYPE_SKIP_CTX):
            return False
        if not ctx.get(MIEN_LEAVE_TYPE_FILTER_CTX):
            return False
        return bool(self._get_employee_id_for_mien_filter())

    @api.model
    def _domain_with_employee_mien(self, domain):
        if not self._should_apply_mien_leave_type_filter():
            return domain
        employee_id = self._get_employee_id_for_mien_filter()
        employee = self.env["hr.employee"].browse(employee_id)
        if not employee.exists():
            return domain
        mien_domain = self.env["hr.leave"]._leave_type_domain_for_employee(employee)
        return Domain(domain or []) & Domain(mien_domain)

    @api.model
    @api.readonly
    def web_name_search(self, name, specification, domain=None, operator="ilike", limit=100):
        domain = self._domain_with_employee_mien(domain)
        return super().web_name_search(
            name, specification, domain=domain, operator=operator, limit=limit
        )
