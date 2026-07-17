# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import datetime, time, timedelta

from odoo import api, fields, models


class LugTaskDashboard(models.AbstractModel):
    _name = "lug.task.dashboard"
    _description = "Dashboard Giao việc IT"

    @api.model
    def _user_role(self):
        user = self.env.user
        if user.has_group("lug_task_assignment.group_lug_task_board"):
            return "board"
        if user.has_group("lug_task_assignment.group_lug_task_manager"):
            return "manager"
        if user.has_group("lug_task_assignment.group_lug_task_team_lead"):
            return "team_lead"
        return "employee"

    @api.model
    def _parse_filters(self, filters=None):
        filters = filters or {}
        today = fields.Date.context_today(self)
        return {
            "year": int(filters.get("year") or today.year),
            "month": int(filters.get("month") or today.month),
            "mien_zone_id": int(filters["mien_zone_id"]) if filters.get("mien_zone_id") else False,
            "department_id": int(filters["department_id"]) if filters.get("department_id") else False,
            "store_id": int(filters["store_id"]) if filters.get("store_id") else False,
        }

    @api.model
    def _task_domain(self, filters):
        domain = []
        if filters.get("mien_zone_id"):
            domain.append(("mien_zone_id", "child_of", filters["mien_zone_id"]))
        if filters.get("department_id"):
            domain.append(("department_id", "child_of", filters["department_id"]))
        if filters.get("store_id"):
            domain.append(("store_id", "=", filters["store_id"]))
        return domain

    @api.model
    def _today_bounds(self):
        today = fields.Date.context_today(self)
        start = datetime.combine(today, time.min)
        end = datetime.combine(today, time.max)
        return start, end

    @api.model
    def _kpi_counts(self, tasks):
        today_start, today_end = self._today_bounds()
        now = fields.Datetime.now()
        soon = now + timedelta(hours=48)
        return {
            "total": len(tasks),
            "completed": len(tasks.filtered(lambda t: t.state in ("completed", "closed"))),
            "overdue": len(tasks.filtered(lambda t: t.is_overdue)),
            "in_progress": len(tasks.filtered(lambda t: t.state == "in_progress")),
            "pending_review": len(tasks.filtered(lambda t: t.state == "review")),
            "pending_approval": len(tasks.filtered(lambda t: t.state in ("draft", "approved"))),
            "today": len(
                tasks.filtered(
                    lambda t: t.due_date and today_start <= t.due_date <= today_end
                )
            ),
            "due_soon": len(
                tasks.filtered(
                    lambda t: t.due_date
                    and now <= t.due_date <= soon
                    and t.state not in ("completed", "closed")
                )
            ),
        }

    @api.model
    def _group_count(self, tasks, field_name, label_fn=None):
        field = tasks._fields.get(field_name)
        is_relational = bool(field) and field.relational
        selection_labels = {}
        if bool(field) and field.type == "selection":
            selection_labels = dict(field._description_selection(self.env))
        buckets = defaultdict(int)
        for task in tasks:
            value = task[field_name]
            if is_relational:
                if not value:
                    key, label = False, "Khác"
                else:
                    key = value.id
                    label = label_fn(value) if label_fn else value.display_name
            else:
                if value in (False, None, ""):
                    key, label = False, "Khác"
                else:
                    key = value
                    label = selection_labels.get(value, str(value))
            buckets[(key, label)] += 1
        result = [
            {"id": key, "label": label, "count": count}
            for (key, label), count in sorted(buckets.items(), key=lambda x: -x[1])
        ]
        return result[:15]

    @api.model
    def _top_employees(self, tasks, limit=10):
        buckets = defaultdict(lambda: {"points": 0.0, "count": 0, "name": ""})
        for task in tasks.filtered(lambda t: t.assigned_to_id and t.state in ("completed", "closed")):
            emp = task.assigned_to_id
            bucket = buckets[emp.id]
            bucket["name"] = emp.name
            bucket["points"] += task.point
            bucket["count"] += 1
        rows = sorted(buckets.values(), key=lambda r: (-r["points"], -r["count"]))
        return rows[:limit]

    @api.model
    def _top_overdue(self, tasks, limit=10):
        overdue = tasks.filtered(lambda t: t.is_overdue).sorted(
            key=lambda t: t.due_date or fields.Datetime.now()
        )
        return [
            {
                "id": t.id,
                "task_code": t.task_code,
                "title": t.title,
                "assignee": t.assigned_to_id.name or "",
                "due_date": t.due_date.strftime("%d/%m/%Y %H:%M") if t.due_date else "",
                "state": t.state,
            }
            for t in overdue[:limit]
        ]

    @api.model
    def _employee_kpi_score(self):
        employee = self.env.user.sudo().employee_id
        if not employee:
            return 0.0
        today = fields.Date.context_today(self)
        kpi = self.env["lug.task.kpi.monthly"].search(
            [
                ("employee_id", "=", employee.id),
                ("year", "=", today.year),
                ("month", "=", today.month),
            ],
            limit=1,
        )
        return round(kpi.score, 1) if kpi else 0.0

    @api.model
    def get_dashboard_data(self, filters=None):
        filters = self._parse_filters(filters)
        role = self._user_role()
        Task = self.env["lug.task"]
        domain = self._task_domain(filters)
        tasks = Task.search(domain)
        kpi = self._kpi_counts(tasks)
        kpi["my_kpi_score"] = self._employee_kpi_score()

        data = {
            "role": role,
            "filters": filters,
            "kpi": kpi,
            "by_mien": [],
            "by_store": [],
            "by_department": [],
            "top_employees": [],
            "top_overdue": self._top_overdue(tasks),
            "employee_performance": [],
            "status_breakdown": self._group_count(tasks, "state"),
        }

        if role in ("board", "manager", "team_lead"):
            data["by_mien"] = self._group_count(tasks, "mien_zone_id")
            data["by_store"] = self._group_count(
                tasks, "store_id", lambda s: s.code or s.name
            )
            data["by_department"] = self._group_count(tasks, "department_id")

        if role in ("board", "manager"):
            data["top_employees"] = self._top_employees(tasks)

        if role in ("manager", "team_lead"):
            perf = defaultdict(lambda: {"name": "", "open": 0, "done": 0, "overdue": 0})
            for task in tasks:
                emp = task.assigned_to_id
                if not emp:
                    continue
                row = perf[emp.id]
                row["name"] = emp.name
                if task.state in ("completed", "closed"):
                    row["done"] += 1
                elif task.is_overdue:
                    row["overdue"] += 1
                else:
                    row["open"] += 1
            data["employee_performance"] = sorted(
                perf.values(), key=lambda r: (-r["overdue"], -r["open"])
            )[:20]

        return data

    @api.model
    def get_filter_options(self):
        return {
            "miens": [
                {"id": z.id, "name": z.name}
                for z in self.env["hr.mien.zone"].search([("is_assignable", "=", True)])
            ],
            "departments": [
                {"id": d.id, "name": d.name}
                for d in self.env["hr.department"].search([], limit=200)
            ],
            "stores": [
                {"id": s.id, "name": s.code or s.name}
                for s in self.env["hr.store"].search([("active", "=", True)], limit=300)
            ],
        }
