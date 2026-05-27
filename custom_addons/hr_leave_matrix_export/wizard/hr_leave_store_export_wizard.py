# Part of Odoo. See LICENSE file for full copyright and licensing details.

import calendar
import json
from datetime import date, datetime
from io import BytesIO

import xlsxwriter

from odoo import _, api, fields, models
from odoo.exceptions import UserError

STORE_HEADERS = [
    "MIỀN",
    "ID NHÂN VIÊN",
    "TÊN NHÂN VIÊN",
    "MÃ BỘ PHẬN",
    "CHỨC VỤ",
    "Ngày tạo đơn",
    "NGÀY NGHỈ Bắt đầu",
    "Ngày nghỉ kết thúc",
    "SỐ NGÀY NGHỈ",
    "LÝ DO NGHỈ",
    "NGƯỜI NHẬN BÀN GIAO",
    "ASM DUYỆT",
    "NGÀY ASM DUYỆT",
    "AD DUYỆT",
    "NGÀY AD DUYỆT",
    "trạng thái",
]

MIEN_DISPLAY = {
    "Bắc": "BẮC",
    "Nam": "NAM",
    "ĐTT": "ĐTT",
    "VP": "VP",
}

JOB_TITLE_SHORT = {
    "cửa hàng trưởng": "CHT",
    "asm": "ASM",
    "rsm": "RSM",
    "nhân viên ch": "NVCH",
    "nhân viên vp": "NVVP",
    "trưởng nhóm": "TN",
    "giám sát": "GS",
    "admin": "AD",
    "admin tổng": "AD",
}

_EMERGENCY_STATUS_TEXT = (
    "Bạn đang gửi đơn nghỉ khẩn cấp (thời gian báo trước ngắn hơn quy định). "
    "Bạn có chắc chắn muốn tiếp tục không?"
)


class HrLeaveStoreExportMixin(models.AbstractModel):
    """Store form Excel export (used via hr.leave.matrix.export.wizard)."""

    _name = "hr.leave.store.export.mixin"
    _description = "Export store time off (FORM KẾT XUẤT NGHỈ PHÉP)"

    @staticmethod
    def _format_date(value):
        if not value:
            return ""
        if isinstance(value, datetime):
            value = value.date()
        if isinstance(value, date):
            return f"{value.day}/{value.month}/{value.year}"
        return str(value)

    def _is_store_leave(self, leave):
        """Store export: vp_chain flow (cửa hàng trưởng chain)."""
        if leave.validation_type != "vp_chain":
            return False
        if hasattr(leave, "_is_store_chain_flow"):
            return leave._is_store_chain_flow()
        emp = leave.employee_id
        return bool(emp and (emp.job_title or "") == "cửa hàng trưởng")

    def _mien_label(self, employee):
        mien = getattr(employee, "mien", None) or ""
        return MIEN_DISPLAY.get(mien, (mien or "").upper())

    def _job_title_code(self, employee):
        if not employee:
            return ""
        ma = (getattr(employee, "ma_chuc_vu", None) or "").strip()
        if ma:
            return ma.upper()
        jt = employee.job_title or ""
        if jt in JOB_TITLE_SHORT:
            return JOB_TITLE_SHORT[jt]
        if "job_title" in employee._fields and employee._fields["job_title"].type == "selection":
            labels = dict(employee._fields["job_title"]._description_selection(self.env))
            label = labels.get(jt, jt)
            return (label or "").upper()
        return jt.upper()

    def _handover_recipient_names(self, leave):
        if "handover_acceptance_ids" not in leave._fields:
            return ""
        lines = leave.handover_acceptance_ids
        if not lines:
            return ""
        names = lines.mapped("employee_id.name")
        return ", ".join(n for n in names if n)

    def _approval_for_job_title(self, leave, job_title_keys):
        """Return (approver display name, approval date str) from responsible approval lines."""
        if isinstance(job_title_keys, str):
            job_title_keys = (job_title_keys,)
        if "responsible_approval_line_ids" not in leave._fields:
            return "", ""
        lines = leave.responsible_approval_line_ids.sorted("sequence")

        def _matches(line):
            emp = line.user_id.employee_id
            return emp and (emp.job_title or "") in job_title_keys

        approved = lines.filtered(lambda line: line.state == "approved" and _matches(line))
        if approved:
            line = approved[0]
            emp = line.user_id.employee_id
            name = (emp.name or line.user_id.name or "").upper()
            return name, self._format_date(line.action_date)
        pending = lines.filtered(lambda line: line.state == "pending" and _matches(line))
        if pending:
            line = pending[0]
            emp = line.user_id.employee_id
            return (emp.name or line.user_id.name or "").upper(), ""
        return "", ""

    def _status_text(self, leave):
        if getattr(leave, "is_emergency_leave", False):
            return _EMERGENCY_STATUS_TEXT
        if getattr(leave, "status_display_label", None):
            return leave.status_display_label
        return dict(leave._fields["state"].selection).get(leave.state, leave.state or "")

    def _leave_reason(self, leave):
        return (leave.private_name or leave.name or "").strip()

    def _row_for_leave(self, leave):
        emp = leave.employee_id
        asm_name, asm_date = self._approval_for_job_title(leave, ("asm",))
        ad_name, ad_date = self._approval_for_job_title(leave, ("admin tổng", "admin"))
        return [
            self._mien_label(emp) if emp else "",
            (getattr(emp, "id_hrm", None) or "").strip() if emp else "",
            (emp.name or "").upper() if emp else "",
            (getattr(emp, "ma_bo_phan", None) or "").strip().upper() if emp else "",
            self._job_title_code(emp),
            self._format_date(leave.create_date),
            self._format_date(leave.request_date_from),
            self._format_date(leave.request_date_to),
            leave.number_of_days or "",
            self._leave_reason(leave),
            self._handover_recipient_names(leave),
            asm_name,
            asm_date,
            ad_name,
            ad_date,
            self._status_text(leave),
        ]

    def _search_store_leaves(self, year, month, base_domain):
        last_day = calendar.monthrange(year, month)[1]
        month_start = date(year, month, 1)
        month_end = date(year, month, last_day)
        overlap = [
            ("request_date_from", "<=", month_end),
            ("request_date_to", ">=", month_start),
        ]
        domain = base_domain + overlap if base_domain else overlap
        leaves = self.env["hr.leave"].search(
            domain,
            order="employee_id, request_date_from, id",
        )
        return leaves.filtered(lambda leave: self._is_store_leave(leave))

    def action_export_store_excel(self):
        self.ensure_one()
        if not self.env.user.has_group("base.group_allow_export"):
            raise UserError(_("You need export permissions to download this file."))

        year, month = int(self.year), int(self.month)
        leaves = self._search_store_leaves(year, month, self._parse_domain())

        buffer = BytesIO()
        workbook = xlsxwriter.Workbook(buffer, {"in_memory": True})
        sheet = workbook.add_worksheet("Nghỉ phép CH")

        title_fmt = workbook.add_format(
            {"bold": True, "font_size": 12, "align": "center", "valign": "vcenter"}
        )
        header_fmt = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#BDD7EE",
                "border": 1,
                "align": "center",
                "text_wrap": True,
                "valign": "vcenter",
            }
        )
        cell_fmt = workbook.add_format({"border": 1, "valign": "top", "text_wrap": True})
        status_fmt = workbook.add_format({"border": 1, "valign": "top", "text_wrap": True})

        sheet.merge_range(0, 0, 0, len(STORE_HEADERS) - 1, "FORM KẾT XUẤT NGHỈ PHÉP", title_fmt)
        for col, title in enumerate(STORE_HEADERS):
            sheet.write(1, col, title, header_fmt)

        row = 2
        for leave in leaves:
            values = self._row_for_leave(leave)
            for col, value in enumerate(values):
                fmt = status_fmt if col == len(STORE_HEADERS) - 1 else cell_fmt
                sheet.write(row, col, value, fmt)
            row += 1

        if row == 2:
            sheet.write_row(2, 0, [""] * len(STORE_HEADERS), cell_fmt)
            row = 3

        sheet.freeze_panes(2, 0)
        sheet.set_column(0, 0, 8)
        sheet.set_column(1, 1, 12)
        sheet.set_column(2, 2, 28)
        sheet.set_column(3, 4, 12)
        sheet.set_column(5, 8, 14)
        sheet.set_column(9, 9, 32)
        sheet.set_column(10, 10, 28)
        sheet.set_column(11, 14, 18)
        sheet.set_column(15, 15, 55)

        workbook.close()
        buffer.seek(0)
        filename = "form_ket_xuat_nghi_phep_ch_%s-%02d.xlsx" % (year, month)

        attachment = self.env["ir.attachment"].create(
            {
                "name": filename,
                "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "raw": buffer.read(),
                "res_model": self._name,
                "res_id": self.id,
            }
        )
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % attachment.id,
            "target": "self",
        }
