# -*- coding: utf-8 -*-

from odoo import api, fields, models


class LugUserMonthSummary(models.Model):
    _name = "lug.user.month.summary"
    _description = "Lug Security Monthly Summary"
    _order = "year desc, month desc, user_id"
    _rec_name = "month_label"

    year = fields.Integer(string="Năm", required=True, index=True)
    month = fields.Integer(string="Tháng", required=True, index=True)
    month_label = fields.Char(string="Kỳ", compute="_compute_month_label", store=True)
    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        ondelete="cascade",
        index=True,
    )
    employee_id = fields.Many2one(
        "hr.employee",
        string="Nhân viên",
        related="user_id.employee_id",
        store=True,
        readonly=True,
    )
    employee_name = fields.Char(
        string="Họ tên",
        related="employee_id.name",
        readonly=True,
    )
    job_id = fields.Many2one(
        "hr.job",
        string="Chức danh",
        related="employee_id.job_id",
        readonly=True,
    )
    department_id = fields.Many2one(
        "hr.department",
        string="Phòng ban",
        related="employee_id.department_id",
        readonly=True,
    )
    mien_label = fields.Char(
        string="Miền",
        compute="_compute_org_labels",
    )
    total_login_days = fields.Integer(string="Số ngày Login")
    total_minutes = fields.Integer(string="Tổng phút")
    total_sessions = fields.Integer(string="Số phiên")
    average_minutes = fields.Integer(string="TB phút/ngày")
    device_count = fields.Integer(string="Số thiết bị")
    total_hours_display = fields.Char(
        string="Tổng giờ",
        compute="_compute_display_metrics",
    )
    average_hours_display = fields.Char(
        string="TB/ngày",
        compute="_compute_display_metrics",
    )

    _month_user_uniq = models.Constraint(
        "UNIQUE(year, month, user_id)",
        "Mỗi user chỉ có một bản ghi tổng hợp cho mỗi tháng.",
    )

    @api.depends("year", "month")
    def _compute_month_label(self):
        for rec in self:
            rec.month_label = f"{rec.month:02d}/{rec.year}" if rec.year and rec.month else ""

    @api.depends("employee_id")
    def _compute_org_labels(self):
        Employee = self.env["hr.employee"]
        for rec in self:
            employee = rec.employee_id
            if not employee:
                rec.mien_label = False
                continue
            if "mien_zone_id" in Employee._fields and employee.mien_zone_id:
                zone = employee.mien_zone_id
                rec.mien_label = getattr(zone, "legacy_mien", False) or zone.display_name
            elif "mien" in Employee._fields:
                rec.mien_label = employee.mien
            else:
                rec.mien_label = False

    @api.depends("total_minutes", "average_minutes")
    def _compute_display_metrics(self):
        for rec in self:
            rec.total_hours_display = f"{(rec.total_minutes or 0) / 60:.0f}h"
            rec.average_hours_display = f"{(rec.average_minutes or 0) / 60:.1f}h"
