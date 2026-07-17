# -*- coding: utf-8 -*-

import base64
import io

from odoo import _, fields, models
from odoo.exceptions import UserError

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class LugTaskExportWizard(models.TransientModel):
    _name = "lug.task.export.wizard"
    _description = "Xuất Excel công việc / mẫu import"

    file_data = fields.Binary(string="File", readonly=True)
    file_name = fields.Char(string="Tên file", readonly=True)
    state = fields.Selection([("ready", "Sẵn sàng"), ("done", "Xong")], default="ready")

    def _build_workbook(self, rows, sheet_name="Tasks"):
        if not xlsxwriter:
            raise UserError(_("Thiếu thư viện xlsxwriter."))
        buffer = io.BytesIO()
        wb = xlsxwriter.Workbook(buffer, {"in_memory": True})
        ws = wb.add_worksheet(sheet_name[:31])
        header_fmt = wb.add_format({"bold": True, "bg_color": "#D9E1F2"})
        headers = list(rows[0].keys()) if rows else [
            "title", "category_code", "priority_code", "assigned_to",
            "due_date", "estimate_hours", "description", "point",
        ]
        for col, header in enumerate(headers):
            ws.write(0, col, header, header_fmt)
            ws.set_column(col, col, max(14, len(header) + 2))
        for row_idx, row in enumerate(rows, start=1):
            for col, header in enumerate(headers):
                ws.write(row_idx, col, row.get(header, ""))
        wb.close()
        return buffer.getvalue()

    def action_export_template(self):
        sample = [
            {
                "title": "Cài máy POS cửa HCM",
                "category_code": "install",
                "priority_code": "high",
                "assigned_to": "Mã NV / email / tên",
                "due_date": "2026-06-30 17:00",
                "estimate_hours": 2,
                "description": "Ghi chú chi tiết",
                "point": "",
            },
        ]
        data = self._build_workbook(sample, "Mau_import")
        filename = "lug_task_import_template.xlsx"
        self.write(
            {
                "file_data": base64.b64encode(data),
                "file_name": filename,
                "state": "done",
            }
        )
        return self._download_action()

    def action_export_tasks(self):
        tasks = self.env["lug.task"].search([])
        rows = []
        for task in tasks:
            assignee = ""
            if task.assigned_to_id:
                emp = task.assigned_to_id
                assignee = emp.barcode or emp.work_email or emp.name
            rows.append(
                {
                    "task_code": task.task_code,
                    "title": task.title,
                    "category_code": task.category_id.code or "",
                    "priority_code": task.priority_id.code or "",
                    "assigned_to": assignee,
                    "assigned_by": task.assigned_by_id.name or "",
                    "state": task.state,
                    "due_date": task.due_date.strftime("%Y-%m-%d %H:%M") if task.due_date else "",
                    "completed_date": task.completed_date.strftime("%Y-%m-%d %H:%M") if task.completed_date else "",
                    "progress": task.progress,
                    "point": task.point,
                    "actual_hours": task.actual_hours,
                    "is_overdue": task.is_overdue,
                    "department": task.department_id.name or "",
                    "mien": task.mien_zone_id.name or "",
                    "store": task.store_id.code or "",
                }
            )
        data = self._build_workbook(rows or [{"task_code": ""}], "Cong_viec")
        filename = "lug_task_export.xlsx"
        self.write(
            {
                "file_data": base64.b64encode(data),
                "file_name": filename,
                "state": "done",
            }
        )
        return self._download_action()

    def _download_action(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/?model=%s&id=%s&field=file_data&filename=%s&download=true"
            % (self._name, self.id, self.file_name),
            "target": "self",
        }
