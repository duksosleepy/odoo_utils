# -*- coding: utf-8 -*-

from odoo import api, fields, models


class LugTaskKpiMonthly(models.Model):
    _name = "lug.task.kpi.monthly"
    _description = "KPI tháng nhân viên IT"
    _order = "year desc, month desc, score desc"
    _rec_name = "display_name"

    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    year = fields.Integer(string="Năm", required=True, index=True)
    month = fields.Integer(string="Tháng", required=True, index=True)
    display_name = fields.Char(compute="_compute_display_name", store=True)

    # Thành phần KPI (theo đề xuất IT)
    planned_points = fields.Float(string="Điểm kế hoạch", default=0.0)
    completed_points = fields.Float(string="Điểm hoàn thành", default=0.0)
    volume_score = fields.Float(
        string="Khối lượng (40%)",
        compute="_compute_scores",
        store=True,
    )
    on_time_total = fields.Integer(string="Task đúng hạn", default=0)
    on_time_score = fields.Float(
        string="Đúng hạn (25%)",
        compute="_compute_scores",
        store=True,
    )
    total_tasks = fields.Integer(string="Tổng task", default=0)
    defect_tasks = fields.Integer(string="Task lỗi", default=0)
    quality_score = fields.Float(
        string="Chất lượng (20%)",
        compute="_compute_scores",
        store=True,
    )
    initiative_score = fields.Float(
        string="Chủ động (%)",
        default=0.0,
        help="Đánh giá thủ công của quản lý (0–100).",
    )
    process_score = fields.Float(
        string="Báo cáo/quy trình (%)",
        default=100.0,
        help="Tỷ lệ công việc cập nhật đúng quy trình (0–100).",
    )
    score = fields.Float(
        string="Điểm KPI",
        compute="_compute_scores",
        store=True,
    )
    productivity = fields.Float(
        string="Năng suất",
        compute="_compute_productivity",
        store=True,
        help="Tổng điểm / Tổng giờ làm.",
    )
    total_hours = fields.Float(string="Tổng giờ", default=0.0)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )

    _employee_month_unique = models.Constraint(
        "unique(employee_id, year, month, company_id)",
        "Mỗi nhân viên chỉ có một bản ghi KPI cho mỗi tháng.",
    )

    @api.depends("employee_id", "year", "month")
    def _compute_display_name(self):
        for rec in self:
            name = rec.employee_id.name or "?"
            rec.display_name = f"KPI {name} — {rec.month:02d}/{rec.year}"

    @api.model
    def _process_score_for_employee(self, employee, year, month):
        if not employee:
            return 100.0
        if month == 12:
            end = fields.Datetime.to_datetime(f"{year + 1}-01-01")
        else:
            end = fields.Datetime.to_datetime(f"{year}-{month + 1:02d}-01")
        start = fields.Datetime.to_datetime(f"{year}-{month:02d}-01")
        tasks = self.env["lug.task"].search(
            [
                ("assigned_to_id", "=", employee.id),
                ("state", "in", ("completed", "closed")),
                ("completed_date", ">=", start),
                ("completed_date", "<", end),
            ]
        )
        if not tasks:
            return 100.0
        compliant = len(tasks.filtered("process_compliant"))
        return compliant * 100.0 / len(tasks)

    @api.depends(
        "planned_points",
        "completed_points",
        "on_time_total",
        "total_tasks",
        "defect_tasks",
        "initiative_score",
        "process_score",
    )
    def _compute_scores(self):
        for rec in self:
            volume = (
                (rec.completed_points / rec.planned_points * 100.0)
                if rec.planned_points
                else 0.0
            )
            rec.volume_score = min(volume, 100.0) * 0.40

            on_time_pct = (
                (rec.on_time_total / rec.total_tasks * 100.0) if rec.total_tasks else 0.0
            )
            rec.on_time_score = on_time_pct * 0.25

            defect_rate = (
                (rec.defect_tasks / rec.total_tasks) if rec.total_tasks else 0.0
            )
            quality_pct = (1.0 - defect_rate) * 100.0
            rec.quality_score = quality_pct * 0.20

            rec.score = (
                rec.volume_score
                + rec.on_time_score
                + rec.quality_score
                + rec.initiative_score * 0.10
                + rec.process_score * 0.05
            )

    @api.depends("completed_points", "total_hours")
    def _compute_productivity(self):
        for rec in self:
            rec.productivity = (
                rec.completed_points / rec.total_hours if rec.total_hours else 0.0
            )

    @api.model
    def _cron_compute_monthly_kpi(self):
        """Tính KPI tháng hiện tại từ lug.task — chỉ đọc HR, không ghi HR."""
        today = fields.Date.context_today(self)
        year, month = today.year, today.month
        Task = self.env["lug.task"]
        domain = [
            ("state", "in", ("completed", "closed")),
            ("completed_date", "!=", False),
        ]
        tasks = Task.search(domain)
        by_employee = {}
        for task in tasks:
            if not task.assigned_to_id or not task.completed_date:
                continue
            if task.completed_date.month != month or task.completed_date.year != year:
                continue
            emp = task.assigned_to_id
            bucket = by_employee.setdefault(emp.id, {"tasks": [], "employee": emp})
            bucket["tasks"].append(task)

        for emp_id, data in by_employee.items():
            emp_tasks = data["tasks"]
            total = len(emp_tasks)
            on_time = sum(1 for t in emp_tasks if not t.is_overdue)
            defects = sum(1 for t in emp_tasks if t.is_quality_issue)
            completed_pts = sum(t.point for t in emp_tasks)
            hours = sum(t.actual_hours for t in emp_tasks)
            existing = self.search(
                [
                    ("employee_id", "=", emp_id),
                    ("year", "=", year),
                    ("month", "=", month),
                ],
                limit=1,
            )
            vals = {
                "employee_id": emp_id,
                "year": year,
                "month": month,
                "total_tasks": total,
                "on_time_total": on_time,
                "defect_tasks": defects,
                "completed_points": completed_pts,
                "planned_points": completed_pts or 1.0,
                "total_hours": hours,
                "process_score": self._process_score_for_employee(data["employee"], year, month),
            }
            if existing:
                existing.write(vals)
            else:
                self.create(vals)
