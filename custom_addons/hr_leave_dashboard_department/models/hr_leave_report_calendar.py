# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrLeaveReportCalendar(models.Model):
    _inherit = "hr.leave.report.calendar"

    employee_id_hrm = fields.Char(
        string="ID HRM",
        compute="_compute_employee_hrm_info",
        readonly=True,
    )
    employee_ma_bo_phan = fields.Char(
        string="Mã bộ phận",
        compute="_compute_employee_hrm_info",
        readonly=True,
    )
    leave_reason = fields.Text(
        string="Lý do",
        compute="_compute_leave_reason",
        readonly=True,
    )

    @api.depends("employee_id")
    def _compute_employee_hrm_info(self):
        for report in self:
            employee = report.employee_id.sudo()
            id_hrm = (getattr(employee, "id_hrm", None) or "").strip()
            report.employee_id_hrm = f"ID {id_hrm}" if id_hrm else ""
            report.employee_ma_bo_phan = (getattr(employee, "ma_bo_phan", None) or "").strip()

    @api.depends("description", "leave_id")
    def _compute_leave_reason(self):
        for report in self:
            reason = (report.sudo().description or "").strip()
            if not reason and report.leave_id:
                reason = (report.leave_id.sudo().name or "").strip()
            report.leave_reason = reason
