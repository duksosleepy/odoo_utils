# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class HrLeaveAnalyticsReport(models.Model):
    _name = "hr.leave.analytics.report"
    _description = "HR Leave Analytics Report"
    _auto = False
    _order = "request_date_from desc, employee_id, id"
    _rec_name = "employee_name"

    leave_id = fields.Many2one("hr.leave", string="Đơn nghỉ", readonly=True)
    employee_id = fields.Many2one("hr.employee", string="Nhân viên", readonly=True)
    employee_name = fields.Char(string="Họ và tên", readonly=True)
    department_id = fields.Many2one("hr.department", string="Phòng ban", readonly=True)
    employee_mien = fields.Selection(
        selection=[
            ("Bắc", "Miền Bắc"),
            ("Nam", "Miền Nam"),
            ("ĐTT", "Miền ĐTT"),
            ("VP", "VP"),
            ("Tất cả", "Tất cả"),
        ],
        string="Miền",
        readonly=True,
    )
    workforce_block = fields.Selection(
        selection=[
            ("office", "Văn phòng"),
            ("store", "Cửa hàng"),
            ("all", "Tất cả"),
        ],
        string="Khối",
        readonly=True,
    )
    store_id = fields.Many2one("hr.store", string="Cửa hàng", readonly=True)
    store_code = fields.Char(string="Mã cửa hàng", readonly=True)
    store_name = fields.Char(string="Tên cửa hàng", readonly=True)
    holiday_status_id = fields.Many2one("hr.leave.type", string="Loại nghỉ", readonly=True)
    leave_type_name = fields.Char(related="holiday_status_id.name", string="Tên loại nghỉ", readonly=True)
    number_of_days = fields.Float(string="Số ngày nghỉ", readonly=True)
    request_date_from = fields.Date(string="Từ ngày", readonly=True)
    request_date_to = fields.Date(string="Đến ngày", readonly=True)
    leave_month = fields.Date(string="Tháng", readonly=True)
    weekday = fields.Integer(string="Thứ (0=CN)", readonly=True)
    weekday_label = fields.Char(string="Thứ", readonly=True)
    state = fields.Selection(
        selection=[
            ("cancel", "Cancelled"),
            ("confirm", "To Approve"),
            ("refuse", "Refused"),
            ("validate1", "Second Approval"),
            ("validate", "Approved"),
        ],
        string="Trạng thái",
        readonly=True,
    )
    company_id = fields.Many2one("res.company", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "hr_leave_analytics_report")
        self.env.cr.execute(
            """
            CREATE OR REPLACE VIEW hr_leave_analytics_report AS (
                SELECT
                    l.id AS id,
                    l.id AS leave_id,
                    l.employee_id AS employee_id,
                    COALESCE(e.name, '') AS employee_name,
                    v.department_id AS department_id,
                    COALESCE(l.employee_leave_mien, e.mien) AS employee_mien,
                    COALESCE(e.employee_visibility, 'all') AS workforce_block,
                    sc.store_id AS store_id,
                    COALESCE(sc.code, '') AS store_code,
                    COALESCE(sc.code, '') AS store_name,
                    l.holiday_status_id AS holiday_status_id,
                    l.number_of_days AS number_of_days,
                    l.request_date_from AS request_date_from,
                    l.request_date_to AS request_date_to,
                    date_trunc('month', l.request_date_from::timestamp)::date AS leave_month,
                    EXTRACT(DOW FROM l.request_date_from)::integer AS weekday,
                    CASE EXTRACT(DOW FROM l.request_date_from)::integer
                        WHEN 0 THEN 'Chủ nhật'
                        WHEN 1 THEN 'Thứ 2'
                        WHEN 2 THEN 'Thứ 3'
                        WHEN 3 THEN 'Thứ 4'
                        WHEN 4 THEN 'Thứ 5'
                        WHEN 5 THEN 'Thứ 6'
                        WHEN 6 THEN 'Thứ 7'
                    END AS weekday_label,
                    l.state AS state,
                    l.employee_company_id AS company_id
                FROM hr_leave l
                INNER JOIN hr_employee e ON l.employee_id = e.id
                LEFT JOIN hr_version v ON v.id = e.current_version_id
                LEFT JOIN hr_store_code sc ON sc.id = e.ma_bo_phan_id
                WHERE e.active IS TRUE
                  AND l.state != 'cancel'
            )
            """
        )

    def action_open_leave(self):
        self.ensure_one()
        if not self.leave_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.leave",
            "res_id": self.leave_id.id,
            "view_mode": "form",
            "target": "current",
        }

    @api.model
    def _analytics_base_domain(self, filters=None):
        filters = filters or {}
        domain = [("company_id", "in", self.env.companies.ids)]
        date_from = filters.get("date_from")
        date_to = filters.get("date_to")
        if date_from:
            domain.append(("request_date_to", ">=", date_from))
        if date_to:
            domain.append(("request_date_from", "<=", date_to))
        if filters.get("employee_mien"):
            domain.append(("employee_mien", "=", filters["employee_mien"]))
        if filters.get("department_id"):
            domain.append(("department_id", "=", filters["department_id"]))
        if filters.get("store_id"):
            domain.append(("store_id", "=", filters["store_id"]))
        if filters.get("workforce_block"):
            domain.append(("workforce_block", "=", filters["workforce_block"]))
        if filters.get("holiday_status_id"):
            domain.append(("holiday_status_id", "=", filters["holiday_status_id"]))
        return domain
