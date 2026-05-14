# Part of Odoo. See LICENSE file for full copyright and licensing details.

import calendar
import json
from collections import defaultdict
from datetime import date, timedelta
from io import BytesIO

import xlsxwriter

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HrLeaveMatrixExportWizard(models.TransientModel):
    _name = "hr.leave.matrix.export.wizard"
    _description = "Export time off as day matrix (Excel)"

    year = fields.Integer(required=True, default=lambda self: fields.Date.context_today(self).year)
    month = fields.Integer(
        required=True,
        default=lambda self: fields.Date.context_today(self).month,
        help="Calendar month used for columns N1…N(last day).",
    )
    domain_json = fields.Text(
        string="Search domain (JSON)",
        help="Technical: current list filters from the Time Off list view.",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        ctx = self.env.context
        raw = ctx.get("matrix_export_domain_json")
        if raw is not None and "domain_json" in fields_list:
            res["domain_json"] = raw if isinstance(raw, str) else json.dumps(raw)
        return res

    @api.constrains("month")
    def _check_month(self):
        for wiz in self:
            if wiz.month < 1 or wiz.month > 12:
                raise UserError(_("Month must be between 1 and 12."))

    def _parse_domain(self):
        self.ensure_one()
        raw = (self.domain_json or "").strip()
        if not raw:
            return []
        try:
            domain = json.loads(raw)
        except json.JSONDecodeError as e:
            raise UserError(_("Invalid search domain: %s") % e) from e
        if not isinstance(domain, list):
            raise UserError(_("Search domain must be a list."))
        return domain

    @staticmethod
    def _leave_type_cell_label(leave_type):
        if not leave_type:
            return ""
        name = (leave_type.name or "").strip()
        if not name:
            return ""
        if len(name) <= 5:
            return name.upper()
        return (name[:4].rstrip() + ".").upper()

    def _build_matrix(self, year, month, base_domain):
        last_day = calendar.monthrange(year, month)[1]
        month_start = date(year, month, 1)
        month_end = date(year, month, last_day)
        overlap_domain = [
            ("request_date_from", "<=", month_end),
            ("request_date_to", ">=", month_start),
        ]
        domain = base_domain + overlap_domain if base_domain else overlap_domain
        leaves = self.env["hr.leave"].search(domain, order="employee_id, request_date_from, id")

        # day (1..31) -> employee_id -> ordered unique labels
        cells = defaultdict(lambda: defaultdict(list))
        employees = self.env["hr.employee"]
        for leave in leaves:
            if not leave.employee_id or not leave.request_date_from or not leave.request_date_to:
                continue
            employees |= leave.employee_id
            label = self._leave_type_cell_label(leave.holiday_status_id)
            if not label:
                label = "L"
            span_start = max(leave.request_date_from, month_start)
            span_end = min(leave.request_date_to, month_end)
            d = span_start
            while d <= span_end:
                bucket = cells[d.day][leave.employee_id.id]
                if label not in bucket:
                    bucket.append(label)
                d += timedelta(days=1)

        return employees, cells, last_day

    def action_export_matrix_excel(self):
        self.ensure_one()
        if not self.env.user.has_group("base.group_allow_export"):
            raise UserError(_("You need export permissions to download this file."))

        year, month = int(self.year), int(self.month)
        base_domain = self._parse_domain()
        employees, cells, last_day = self._build_matrix(year, month, base_domain)
        employees = employees.sorted(lambda e: (e.name or ""))

        buffer = BytesIO()
        workbook = xlsxwriter.Workbook(buffer, {"in_memory": True})
        sheet = workbook.add_worksheet(_("Time off"))

        header_fmt = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#BDD7EE",  # xanh nhạt, dễ đọc hơn xám
                "font_color": "#000000",
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "text_wrap": True,
            }
        )
        name_header = "HỌ VÀ TÊN (dấu)"
        # add_table() always rewrites the header row; without explicit "columns" it uses "Column1", "Column2", …
        table_columns = [{"header": name_header, "header_format": header_fmt}]
        for day in range(1, last_day + 1):
            table_columns.append({"header": f"N{day}", "header_format": header_fmt})

        name_cell_fmt = workbook.add_format({"text_wrap": True, "valign": "top"})

        row = 1
        for emp in employees:
            sheet.write(row, 0, emp.name or "", name_cell_fmt)
            for day in range(1, last_day + 1):
                labels = cells[day].get(emp.id) or []
                sheet.write(row, day, ", ".join(labels) if labels else "")
            row += 1

        # xlsxwriter add_table() with header_row=True requires at least one data row
        # (otherwise it returns -2 and no Table is written — only headers).
        if row == 1:
            sheet.write_row(1, 0, [""] * (last_day + 1))
            row = 2

        sheet.freeze_panes(1, 0)

        last_row_idx = row - 1
        last_col_idx = last_day  # A = name, B.. = N1..N(last_day)
        table_name = "TimeOffMatrix_%s_%02d" % (year, month)
        ret = sheet.add_table(
            0,
            0,
            last_row_idx,
            last_col_idx,
            {
                "name": table_name[:250],
                "style": "Table Style Medium 9",
                "autofilter": True,
                "banded_rows": True,
                "columns": table_columns,
            },
        )
        if ret != 0:
            raise UserError(
                _("Could not create the Excel table (internal error %s). Try upgrading xlsxwriter.") % ret
            )

        # Độ rộng cột: cột họ tên đủ cho "HỌ VÀ TÊN (dấu)" + nút lọc; các cột N* hẹp vì mã ngắn
        sheet.set_column(0, 0, 38)
        if last_day >= 1:
            sheet.set_column(1, last_day, 7)

        workbook.close()
        buffer.seek(0)
        data = buffer.read()
        filename = "time_off_matrix_%s-%02d.xlsx" % (year, month)

        attachment = self.env["ir.attachment"].create(
            {
                "name": filename,
                "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "raw": data,
                "res_model": self._name,
                "res_id": self.id,
            }
        )
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % attachment.id,
            "target": "self",
        }
