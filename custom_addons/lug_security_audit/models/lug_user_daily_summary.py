# -*- coding: utf-8 -*-

from odoo import api, fields, models


class LugUserDailySummary(models.Model):
    _name = "lug.user.daily.summary"
    _description = "Lug Security Daily Summary"
    _order = "summary_date desc, user_id"
    _rec_name = "summary_date"

    summary_date = fields.Date(string="Ngày", required=True, index=True)
    summary_date_display = fields.Char(
        string="Ngày",
        compute="_compute_summary_date_display",
    )
    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        ondelete="cascade",
        index=True,
    )
    department_id = fields.Many2one("hr.department", string="Phòng ban", ondelete="set null")
    mien_label = fields.Char(string="Miền")
    job_title_label = fields.Char(string="Chức danh")
    login_count = fields.Integer(string="Số lần login")
    total_minutes = fields.Integer(string="Tổng phút")
    total_sessions = fields.Integer(string="Số phiên")
    first_login = fields.Datetime(string="Login đầu")
    first_login_display = fields.Char(
        string="Login đầu",
        compute="_compute_datetime_displays",
    )
    last_logout = fields.Datetime(string="Logout cuối")
    last_logout_display = fields.Char(
        string="Logout cuối",
        compute="_compute_datetime_displays",
    )
    total_hours_display = fields.Char(
        string="Tổng giờ",
        compute="_compute_total_hours_display",
    )

    _date_user_uniq = models.Constraint(
        "UNIQUE(summary_date, user_id)",
        "Mỗi user chỉ có một bản ghi tổng hợp cho mỗi ngày.",
    )

    @api.depends("summary_date")
    def _compute_summary_date_display(self):
        for rec in self:
            rec.summary_date_display = (
                rec.summary_date.strftime("%d/%m/%Y") if rec.summary_date else ""
            )

    @api.depends("first_login", "last_logout")
    def _compute_datetime_displays(self):
        for rec in self:
            rec.first_login_display = rec._format_user_datetime(rec.first_login)
            rec.last_logout_display = rec._format_user_datetime(rec.last_logout)

    def _format_user_datetime(self, dt_value):
        if not dt_value:
            return ""
        local_dt = fields.Datetime.context_timestamp(self, dt_value)
        return local_dt.strftime("%H:%M %d/%m/%Y")

    @api.depends("total_minutes")
    def _compute_total_hours_display(self):
        for rec in self:
            hours = (rec.total_minutes or 0) / 60.0
            rec.total_hours_display = f"{hours:.1f}h"
