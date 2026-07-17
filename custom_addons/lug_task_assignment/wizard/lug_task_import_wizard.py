# -*- coding: utf-8 -*-

import base64
import csv
import io
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError

try:
    import openpyxl
except ImportError:
    openpyxl = None

IMPORT_COLUMNS = (
    "title",
    "category_code",
    "priority_code",
    "assigned_to",
    "due_date",
    "estimate_hours",
    "description",
    "point",
)


class LugTaskImportWizard(models.TransientModel):
    _name = "lug.task.import.wizard"
    _description = "Import công việc từ Excel/CSV"

    file_data = fields.Binary(string="File Excel/CSV", required=True)
    file_name = fields.Char(string="Tên file")
    state = fields.Selection(
        [("upload", "Tải lên"), ("done", "Hoàn tất")],
        default="upload",
    )
    result_message = fields.Html(string="Kết quả", readonly=True)
    created_count = fields.Integer(readonly=True)

    def action_download_template(self):
        export_wizard = self.env["lug.task.export.wizard"].create({})
        return export_wizard.action_export_template()

    @api.model
    def _parse_due_date(self, raw):
        if not raw:
            return False
        if isinstance(raw, datetime):
            return raw
        text = str(raw).strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M", "%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue
        raise UserError(_("Không đọc được ngày hạn: %s") % text)

    @api.model
    def _rows_from_csv(self, content):
        for encoding in ("utf-8-sig", "utf-8", "cp1258", "latin-1"):
            try:
                text = content.decode(encoding)
                break
            except UnicodeDecodeError:
                text = None
        if text is None:
            raise UserError(_("Không đọc được file CSV (lỗi mã hóa)."))
        reader = csv.DictReader(io.StringIO(text))
        return list(reader)

    @api.model
    def _rows_from_xlsx(self, content):
        if not openpyxl:
            raise UserError(_("Thiếu thư viện openpyxl để đọc file Excel."))
        wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        ws = wb.active
        rows_iter = ws.iter_rows(values_only=True)
        headers = [str(h or "").strip().lower() for h in next(rows_iter, [])]
        if not headers:
            raise UserError(_("File Excel không có dòng tiêu đề."))
        rows = []
        for line in rows_iter:
            if not any(line):
                continue
            row = {}
            for idx, header in enumerate(headers):
                if header and idx < len(line):
                    row[header] = line[idx]
            rows.append(row)
        wb.close()
        return rows

    @api.model
    def _normalize_row(self, row):
        normalized = {}
        for key, value in row.items():
            if key is None:
                continue
            normalized[str(key).strip().lower()] = value
        return normalized

    @api.model
    def _find_employee(self, token):
        token = (token or "").strip()
        if not token:
            return False
        Employee = self.env["hr.employee"].sudo()
        domain_variants = [
            [("barcode", "=", token)],
            [("work_email", "=", token)],
        ]
        if "ma_nv_ke_toan" in Employee._fields:
            domain_variants.append([("ma_nv_ke_toan", "=", token)])
        for domain in domain_variants:
            emp = Employee.search(domain, limit=1)
            if emp:
                return emp
        emp = Employee.search([("name", "ilike", token)], limit=1)
        return emp or False

    @api.model
    def _build_task_vals(self, row, assigner):
        row = self._normalize_row(row)
        title = (row.get("title") or row.get("tiêu đề") or "").strip()
        if not title:
            raise UserError(_("Thiếu tiêu đề công việc."))
        cat_code = (row.get("category_code") or row.get("loại việc") or "").strip().lower()
        pri_code = (row.get("priority_code") or row.get("mức độ") or "medium").strip().lower()
        category = self.env["lug.task.category"].search([("code", "=", cat_code)], limit=1)
        if not category:
            raise UserError(_("Không tìm thấy loại việc mã '%s'.") % cat_code)
        priority = self.env["lug.task.priority"].search([("code", "=", pri_code)], limit=1)
        if not priority:
            raise UserError(_("Không tìm thấy mức độ mã '%s'.") % pri_code)
        assignee_token = row.get("assigned_to") or row.get("người nhận") or ""
        assignee = self._find_employee(assignee_token)
        if not assignee:
            raise UserError(_("Không tìm thấy nhân viên: %s") % assignee_token)
        vals = {
            "title": title,
            "category_id": category.id,
            "priority_id": priority.id,
            "assigned_by_id": assigner.id if assigner else False,
            "assigned_to_id": assignee.id,
            "description": row.get("description") or row.get("mô tả") or "",
            "estimate_hours": float(row.get("estimate_hours") or row.get("giờ ước tính") or 0) or 0.0,
            "state": "draft",
        }
        due_raw = row.get("due_date") or row.get("hạn")
        if due_raw:
            vals["due_date"] = self._parse_due_date(due_raw)
        point_raw = row.get("point") or row.get("điểm")
        if point_raw not in (None, ""):
            vals["point"] = float(point_raw)
        return vals

    def action_import(self):
        self.ensure_one()
        if not self.file_data:
            raise UserError(_("Chọn file để import."))
        content = base64.b64decode(self.file_data)
        name = (self.file_name or "").lower()
        if name.endswith(".xlsx") or name.endswith(".xls"):
            rows = self._rows_from_xlsx(content)
        else:
            rows = self._rows_from_csv(content)
        if not rows:
            raise UserError(_("File không có dữ liệu."))
        assigner = self.env.user.sudo().employee_id
        Task = self.env["lug.task"]
        created = Task.browse()
        errors = []
        for idx, row in enumerate(rows, start=2):
            try:
                vals = self._build_task_vals(row, assigner)
                created |= Task.create(vals)
            except UserError as err:
                errors.append(_("Dòng %(row)s: %(msg)s") % {"row": idx, "msg": err.args[0]})
        msg_parts = [
            "<p><b>%s</b> công việc đã được tạo ở trạng thái Nháp.</p>" % len(created),
        ]
        if errors:
            msg_parts.append("<p><b>Lỗi:</b></p><ul>")
            msg_parts.extend("<li>%s</li>" % e for e in errors[:30])
            if len(errors) > 30:
                msg_parts.append("<li>...</li>")
            msg_parts.append("</ul>")
        self.write(
            {
                "state": "done",
                "created_count": len(created),
                "result_message": "".join(msg_parts),
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }
