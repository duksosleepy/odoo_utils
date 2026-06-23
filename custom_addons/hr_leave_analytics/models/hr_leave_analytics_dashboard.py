# Part of Odoo. See LICENSE file for full copyright and licensing details.

from calendar import monthrange
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class HrLeaveAnalyticsDashboard(models.AbstractModel):
    _name = "hr.leave.analytics.dashboard"
    _description = "HR Leave Analytics Dashboard"

    @api.model
    def _default_period(self):
        today = fields.Date.context_today(self)
        start = today.replace(day=1)
        return start, today

    @api.model
    def _parse_filters(self, filters=None):
        filters = filters or {}
        date_from = filters.get("date_from")
        date_to = filters.get("date_to")
        if not date_from or not date_to:
            date_from, date_to = self._default_period()
        return {
            "date_from": fields.Date.to_date(date_from),
            "date_to": fields.Date.to_date(date_to),
            "employee_mien": filters.get("employee_mien") or False,
            "department_id": filters.get("department_id") or False,
            "store_id": filters.get("store_id") or False,
            "workforce_block": filters.get("workforce_block") or False,
            "holiday_status_id": filters.get("holiday_status_id") or False,
        }

    @api.model
    def _employee_domain(self, filters):
        domain = [("active", "=", True), ("company_id", "in", self.env.companies.ids)]
        if filters.get("employee_mien"):
            domain.append(("mien", "=", filters["employee_mien"]))
        if filters.get("department_id"):
            domain.append(("department_id", "=", filters["department_id"]))
        if filters.get("store_id"):
            domain.append(("ma_bo_phan_id.store_id", "=", filters["store_id"]))
        if filters.get("workforce_block"):
            domain.append(("employee_visibility", "=", filters["workforce_block"]))
        return domain

    @api.model
    def _business_days(self, date_from, date_to):
        if not date_from or not date_to or date_from > date_to:
            return 0
        total = 0
        current = date_from
        while current <= date_to:
            if current.weekday() < 5:
                total += 1
            current += relativedelta(days=1)
        return total

    @api.model
    def _read_group_sum(self, model_name, domain, groupby, measure="number_of_days", limit=None):
        field_name = groupby[0] if isinstance(groupby, list) else groupby.split(":")[0]
        rows = self.env[model_name].read_group(
            domain,
            [measure],
            groupby,
            lazy=False,
        )
        result = []
        for row in rows:
            raw = row.get(field_name)
            record_id = False
            label = raw
            if isinstance(raw, tuple):
                record_id = raw[0]
                label = raw[1] or raw[0]
            elif field_name == "employee_mien":
                record_id = raw
            elif field_name == "weekday_label":
                record_id = raw
            result.append(
                {
                    "label": label or "Không xác định",
                    "value": round(row.get(measure, 0.0) or 0.0, 2),
                    "id": record_id,
                }
            )
        result.sort(key=lambda item: item["value"], reverse=True)
        if limit:
            result = result[:limit]
        return result

    @api.model
    def get_dashboard_data(self, filters=None):
        filters = self._parse_filters(filters)
        today = fields.Date.context_today(self)
        Report = self.env["hr.leave.analytics.report"]
        Employee = self.env["hr.employee"]
        Leave = self.env["hr.leave"]

        employee_domain = self._employee_domain(filters)
        total_employees = Employee.search_count(employee_domain)

        base_domain = Report._analytics_base_domain(filters)
        approved_domain = base_domain + [("state", "=", "validate")]
        pending_domain = base_domain + [("state", "in", ("confirm", "validate1"))]

        leave_today = Report.search_count(
            approved_domain
            + [
                ("request_date_from", "<=", today),
                ("request_date_to", ">=", today),
            ]
        )

        month_start = today.replace(day=1)
        month_end = today.replace(day=monthrange(today.year, today.month)[1])
        leave_month_rows = Report.read_group(
            approved_domain
            + [
                ("request_date_from", ">=", month_start),
                ("request_date_from", "<=", month_end),
            ],
            ["number_of_days:sum"],
            [],
        )
        leave_month = round((leave_month_rows[0].get("number_of_days") or 0.0), 2) if leave_month_rows else 0.0

        to_approve = Leave.search_count(
            [
                ("state", "in", ("confirm", "validate1")),
                ("employee_company_id", "in", self.env.companies.ids),
            ]
        )

        period_leave_rows = Report.read_group(approved_domain, ["number_of_days:sum"], [])
        period_leave_days = round(
            (period_leave_rows[0].get("number_of_days") or 0.0) if period_leave_rows else 0.0,
            2,
        )
        business_days = self._business_days(filters["date_from"], filters["date_to"])
        denominator = max(total_employees * business_days, 1)
        leave_rate = round((period_leave_days / denominator) * 100, 2)

        top_leave_rows = self._read_group_sum(
            "hr.leave.analytics.report",
            approved_domain,
            ["employee_id"],
            limit=1,
        )
        top_leave = top_leave_rows[0] if top_leave_rows else {"label": "-", "value": 0.0}

        by_type = self._read_group_sum(
            "hr.leave.analytics.report",
            approved_domain,
            ["holiday_status_id"],
        )
        by_department = self._read_group_sum(
            "hr.leave.analytics.report",
            approved_domain,
            ["department_id"],
            limit=15,
        )
        by_mien = self._read_group_sum(
            "hr.leave.analytics.report",
            approved_domain,
            ["employee_mien"],
        )
        by_workforce = self._read_group_sum(
            "hr.leave.analytics.report",
            approved_domain,
            ["workforce_block"],
        )
        by_store = self._read_group_sum(
            "hr.leave.analytics.report",
            approved_domain,
            ["store_id"],
            limit=10,
        )
        by_month = self._read_group_sum(
            "hr.leave.analytics.report",
            approved_domain,
            ["leave_month"],
        )
        by_month.sort(key=lambda item: item.get("label") or "")
        by_weekday = self._read_group_sum(
            "hr.leave.analytics.report",
            approved_domain,
            ["weekday_label"],
        )
        weekday_order = {
            "Thứ 2": 1,
            "Thứ 3": 2,
            "Thứ 4": 3,
            "Thứ 5": 4,
            "Thứ 6": 5,
            "Thứ 7": 6,
            "Chủ nhật": 7,
        }
        by_weekday.sort(key=lambda item: weekday_order.get(item["label"], 99))

        top_employees = self._read_group_sum(
            "hr.leave.analytics.report",
            approved_domain,
            ["employee_id"],
            limit=10,
        )
        low_balance = self._get_low_balance_employees(filters, threshold=2.0)
        unused_leave = self._get_unused_leave_employees(filters)

        return {
            "filters": {
                "date_from": fields.Date.to_string(filters["date_from"]),
                "date_to": fields.Date.to_string(filters["date_to"]),
                "employee_mien": filters["employee_mien"] or False,
                "department_id": filters["department_id"] or False,
                "store_id": filters["store_id"] or False,
                "workforce_block": filters["workforce_block"] or False,
                "holiday_status_id": filters["holiday_status_id"] or False,
            },
            "kpis": {
                "total_employees": total_employees,
                "leave_today": leave_today,
                "leave_month": leave_month,
                "to_approve": to_approve,
                "leave_rate": leave_rate,
                "top_leave_employee": top_leave,
            },
            "charts": {
                "by_type": by_type,
                "by_department": by_department,
                "by_mien": by_mien,
                "by_workforce": by_workforce,
                "by_store": by_store,
                "by_month": by_month,
                "by_weekday": by_weekday,
            },
            "alerts": {
                "top_employees": top_employees,
                "low_balance": low_balance,
                "unused_leave": unused_leave,
            },
        }

    @api.model
    def _get_low_balance_employees(self, filters, threshold=2.0):
        if "hr.leave.employee.type.report" not in self.env:
            return []
        Report = self.env["hr.leave.employee.type.report"]
        domain = [
            ("company_id", "in", self.env.companies.ids),
            ("holiday_status", "=", "left"),
            ("active_employee", "=", True),
            ("number_of_days", "<=", threshold),
            ("number_of_days", ">", 0),
        ]
        employee_ids = self.env["hr.employee"].search(self._employee_domain(filters)).ids
        if employee_ids:
            domain.append(("employee_id", "in", employee_ids))
        rows = Report.read_group(domain, ["number_of_days:sum"], ["employee_id"], limit=10)
        result = []
        for row in rows:
            employee = row.get("employee_id")
            if not employee:
                continue
            result.append(
                {
                    "label": employee[1],
                    "value": round(row.get("number_of_days") or 0.0, 2),
                    "id": employee[0],
                }
            )
        result.sort(key=lambda item: item["value"])
        return result[:10]

    @api.model
    def _get_unused_leave_employees(self, filters):
        if "hr.leave.employee.type.report" not in self.env:
            return []
        Report = self.env["hr.leave.employee.type.report"]
        employee_ids = self.env["hr.employee"].search(self._employee_domain(filters)).ids
        if not employee_ids:
            return []
        domain = [
            ("company_id", "in", self.env.companies.ids),
            ("holiday_status", "=", "left"),
            ("active_employee", "=", True),
            ("employee_id", "in", employee_ids),
        ]
        rows = Report.read_group(domain, ["number_of_days:sum"], ["employee_id"])
        taken_domain = [
            ("company_id", "in", self.env.companies.ids),
            ("holiday_status", "=", "taken"),
            ("active_employee", "=", True),
            ("employee_id", "in", employee_ids),
        ]
        taken_rows = {
            row["employee_id"][0]: row.get("number_of_days") or 0.0
            for row in Report.read_group(taken_domain, ["number_of_days:sum"], ["employee_id"])
            if row.get("employee_id")
        }
        result = []
        for row in rows:
            employee = row.get("employee_id")
            if not employee:
                continue
            remaining = row.get("number_of_days") or 0.0
            taken = abs(taken_rows.get(employee[0], 0.0))
            if taken <= 0 and remaining >= 5:
                result.append(
                    {
                        "label": employee[1],
                        "value": round(remaining, 2),
                        "id": employee[0],
                    }
                )
        result.sort(key=lambda item: item["value"], reverse=True)
        return result[:10]

    @api.model
    def action_drill_down(self, drill_type, filters=None, record_id=False):
        filters = self._parse_filters(filters)
        Report = self.env["hr.leave.analytics.report"]
        base_domain = Report._analytics_base_domain(filters)

        if drill_type == "to_approve":
            action = self.env.ref("hr_holidays.hr_leave_action_action_approve_department").sudo().read()[0]
            action["domain"] = [("state", "in", ("confirm", "validate1"))]
            return action

        action = self.env.ref("hr_leave_analytics.action_hr_leave_analytics_report").sudo().read()[0]
        domain = list(base_domain)
        today = fields.Date.context_today(self)

        if drill_type == "leave_today":
            domain += [
                ("state", "=", "validate"),
                ("request_date_from", "<=", today),
                ("request_date_to", ">=", today),
            ]
        elif drill_type == "approved_period":
            domain.append(("state", "=", "validate"))
        elif drill_type == "employee" and record_id:
            domain += [("state", "=", "validate"), ("employee_id", "=", record_id)]
        elif drill_type == "leave_type" and record_id:
            domain += [("state", "=", "validate"), ("holiday_status_id", "=", record_id)]
        elif drill_type == "department" and record_id:
            domain += [("state", "=", "validate"), ("department_id", "=", record_id)]
        elif drill_type == "mien" and record_id:
            domain += [("state", "=", "validate"), ("employee_mien", "=", record_id)]
        elif drill_type == "store" and record_id:
            domain += [("state", "=", "validate"), ("store_id", "=", record_id)]
        else:
            domain.append(("state", "=", "validate"))

        action["domain"] = domain
        return action
