# -*- coding: utf-8 -*-

import re
from collections import defaultdict
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


MIEN_ORDER = ["Miền Nam", "Miền DTT", "Miền Bắc", "VPHN"]

MIEN_TO_REGION = {
    "Nam": "Miền Nam",
    "MIỀN NAM": "Miền Nam",
    "Miền Nam": "Miền Nam",
    "ĐTT": "Miền DTT",
    "DTT": "Miền DTT",
    "Miền ĐTT": "Miền DTT",
    "Miền DTT": "Miền DTT",
    "Bắc": "Miền Bắc",
    "MIỀN BẮC": "Miền Bắc",
    "Miền Bắc": "Miền Bắc",
    "VP": "VPHN",
    "VPHN": "VPHN",
    "Văn phòng": "VPHN",
    "Miền VP": "VPHN",
}


class LugEmailDashboard(models.AbstractModel):
    _name = "lug.email.dashboard"
    _description = "Dashboard quản lý tài khoản email"

    @api.model
    def _base_domain(self):
        domain = [("active", "=", True)]
        scope_domain = self.env.user._lug_email_scope_domain()
        if scope_domain:
            domain = ["&"] + domain + scope_domain
        return domain

    @api.model
    def _parse_month_key(self, record):
        text = (record.date_created or "").strip()
        if text:
            for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(text, fmt).strftime("%Y-%m")
                except ValueError:
                    continue
        if record.create_date:
            return fields.Datetime.to_datetime(record.create_date).strftime("%Y-%m")
        return False

    @api.model
    def _month_label(self, month_key):
        try:
            dt = datetime.strptime(month_key, "%Y-%m")
            return dt.strftime("%m/%Y")
        except ValueError:
            return month_key

    @api.model
    def _group_by_label(self, records, label_fn):
        buckets = defaultdict(int)
        for record in records:
            label = label_fn(record) or "Khác"
            buckets[label] += 1
        rows = [{"label": label, "count": count} for label, count in buckets.items()]
        rows.sort(key=lambda row: (-row["count"], row["label"]))
        return rows

    @api.model
    def _monthly_series(self, records, months=12):
        today = fields.Date.context_today(self)
        if hasattr(today, "replace"):
            anchor = today.replace(day=1)
        else:
            anchor = fields.Date.from_string(today).replace(day=1)

        keys = []
        labels = []
        for offset in range(months - 1, -1, -1):
            month_date = anchor - relativedelta(months=offset)
            key = month_date.strftime("%Y-%m")
            keys.append(key)
            labels.append(self._month_label(key))

        buckets = defaultdict(int)
        for record in records:
            month_key = self._parse_month_key(record)
            if month_key:
                buckets[month_key] += 1

        return {
            "labels": labels,
            "counts": [buckets.get(key, 0) for key in keys],
        }

    @api.model
    def _status_kpi(self, records):
        buckets = {"active": 0, "lock": 0, "cancel": 0, "other": 0}
        for record in records:
            code = record.status_code or "other"
            if code not in buckets:
                buckets["other"] += 1
            else:
                buckets[code] += 1
        total = len(records)
        return {
            "total": total,
            "active": buckets["active"],
            "lock": buckets["lock"],
            "cancel": buckets["cancel"],
            "other": buckets["other"],
            "active_percent": round(buckets["active"] * 100 / total, 1) if total else 0,
            "lock_percent": round(buckets["lock"] * 100 / total, 1) if total else 0,
            "cancel_percent": round(buckets["cancel"] * 100 / total, 1) if total else 0,
        }

    @api.model
    def _with_percent(self, rows):
        total = sum(row["count"] for row in rows) or 1
        for row in rows:
            row["percent"] = round(row["count"] * 100 / total, 1)
        return rows

    @api.model
    def _normalize_region_label(self, label):
        raw = (label or "").strip()
        if not raw:
            return False
        if raw in MIEN_TO_REGION:
            return MIEN_TO_REGION[raw]
        folded = raw.casefold()
        for key, value in MIEN_TO_REGION.items():
            if key.casefold() == folded:
                return value
        return False

    @api.model
    def _region_from_department_name(self, name):
        if not name:
            return False
        normalized = self._normalize_region_label(name)
        if normalized:
            return normalized
        upper = name.upper()
        if "VPHN" in upper or "VĂN PHÒNG" in upper or upper.startswith("VP "):
            return "VPHN"
        if "ĐTT" in upper or "DTT" in upper:
            return "Miền DTT"
        if re.search(r"MI[ÊE]N\s*B[ẮA]C", upper) or re.search(r"\bB[ẮA]C\b", upper):
            return "Miền Bắc"
        if re.search(r"MI[ÊE]N\s*NAM", upper) or re.search(r"\bMI[ỀE]N\s*NAM\b", upper):
            return "Miền Nam"
        return False

    @api.model
    def _region_from_department(self, department):
        if not department:
            return False
        current = department
        visited = set()
        while current and current.id not in visited:
            visited.add(current.id)
            region = self._region_from_department_name(current.name)
            if region:
                return region
            current = current.parent_id
        return False

    @api.model
    def _region_for_record(self, record):
        employee = record.employee_id
        if employee:
            if "mien_zone_id" in employee._fields and employee.mien_zone_id:
                zone = employee.mien_zone_id
                for candidate in (
                    getattr(zone, "legacy_mien", False),
                    zone.name,
                    zone.display_name,
                ):
                    region = self._normalize_region_label(candidate)
                    if region:
                        return region
            if "mien" in employee._fields and employee.mien:
                region = self._normalize_region_label(employee.mien)
                if region:
                    return region
        if record.department_id:
            region = self._region_from_department(record.department_id)
            if region:
                return region
        region = self._region_from_department_name(record.department)
        if region:
            return region
        return "Chưa phân loại"

    @api.model
    def _group_by_region(self, records):
        buckets = {label: 0 for label in MIEN_ORDER}
        uncategorized = 0
        for record in records:
            region = self._region_for_record(record)
            if region in buckets:
                buckets[region] += 1
            else:
                uncategorized += 1
        rows = [{"label": label, "count": buckets[label]} for label in MIEN_ORDER]
        if uncategorized:
            rows.append({"label": "Chưa phân loại", "count": uncategorized})
        return rows

    @api.model
    def _region_summary(self, rows, total):
        uncategorized_label = "Chưa phân loại"
        uncategorized = next(
            (row for row in rows if row["label"] == uncategorized_label),
            {"count": 0, "percent": 0},
        )
        classified_count = total - uncategorized["count"]
        classified_total = classified_count or 1
        legend_rows = [row for row in rows if row["label"] != uncategorized_label]
        for row in legend_rows:
            row["share_percent"] = round(row["count"] * 100 / classified_total, 1)
        return {
            "total": total,
            "classified_count": classified_count,
            "uncategorized_count": uncategorized["count"],
            "legend_rows": legend_rows,
        }

    @api.model
    def _sort_department_rows(self, rows):
        uncategorized_label = "Chưa phân loại"
        classified = [row for row in rows if row["label"] != uncategorized_label]
        uncategorized = [row for row in rows if row["label"] == uncategorized_label]
        classified.sort(key=lambda row: (-row["count"], row["label"].casefold()))
        return classified + uncategorized

    @api.model
    def _department_summary(self, rows, total):
        uncategorized_label = "Chưa phân loại"
        uncategorized = next(
            (row for row in rows if row["label"] == uncategorized_label),
            {"count": 0, "percent": 0},
        )
        classified_count = total - uncategorized["count"]
        classified_total = classified_count or 1
        legend_rows = [
            row for row in rows if row["label"] != uncategorized_label
        ]
        legend_rows.sort(key=lambda row: (-row["count"], row["label"].casefold()))
        for row in legend_rows:
            row["share_percent"] = round(row["count"] * 100 / classified_total, 1)
        return {
            "total": total,
            "classified_count": classified_count,
            "uncategorized_count": uncategorized["count"],
            "legend_rows": legend_rows,
        }

    @api.model
    def get_dashboard_data(self):
        emails = self.env["lug.email.account"].search(
            self._base_domain(),
            order="id desc",
        )

        by_department = self._with_percent(
            self._sort_department_rows(
                self._group_by_label(
                    emails,
                    lambda rec: rec.department_id.name or rec.department or "Chưa phân loại",
                )
            )
        )
        by_region = self._with_percent(self._group_by_region(emails))
        by_status = self._with_percent(
            self._group_by_label(
                emails,
                lambda rec: rec.status_id.name if rec.status_id else "Chưa rõ",
            )
        )
        by_month = self._monthly_series(emails)
        kpi = self._status_kpi(emails)
        department_summary = self._department_summary(by_department, kpi["total"])
        region_summary = self._region_summary(by_region, kpi["total"])

        recent_emails = []
        for record in emails[:10]:
            recent_emails.append(
                {
                    "id": record.id,
                    "stt": record.stt or "",
                    "email": record.email or "",
                    "employee_name": record.employee_name or "",
                    "department": record.department_id.name or record.department or "",
                    "status": record.status_id.name if record.status_id else "",
                    "date_created": record.date_created or "",
                }
            )

        return {
            "total": kpi["total"],
            "kpi": kpi,
            "by_department": by_department,
            "department_summary": department_summary,
            "by_region": by_region,
            "region_summary": region_summary,
            "by_status": by_status,
            "by_month": by_month,
            "recent_emails": recent_emails,
        }
