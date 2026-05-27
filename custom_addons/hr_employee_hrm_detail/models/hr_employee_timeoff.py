import logging
from datetime import date

from odoo import api, fields, models
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

# Chỉ trừ phép khi đơn đã duyệt xong (Approved), không trừ khi còn chờ duyệt.
_LEAVES_DEDUCT_STATES = ("validate",)
_CON_LAI_ZERO_CONFIRMED_CTX = "con_lai_zero_confirmed"
_SKIP_CON_LAI_ZERO_CHECK_CTX = "skip_con_lai_zero_check"


class HrEmployeeTimeoff(models.Model):
    _inherit = "hr.employee"

    phep_chuan = fields.Float(string="Phép chuẩn")
    tong_so_phep = fields.Float(string="Tổng số phép")
    da_su_dung = fields.Float(
        string="Số phép đã sử dụng",
        compute="_compute_time_off_summary",
        store=True,
    )
    con_lai = fields.Float(
        string="Số phép còn lại",
        compute="_compute_time_off_summary",
        store=True,
    )
    ngay_het_han = fields.Date(string="Ngày hết hạn")
    con_lai_nam_truoc = fields.Float(
        string="Số phép còn lại năm trước",
        readonly=True,
        help="Số ngày phép còn lại vào cuối năm trước, được hệ thống tự động lưu vào ngày 01/01 hàng năm.",
    )
    nam_chot_con_lai = fields.Integer(
        string="Năm chốt",
        readonly=True,
        help="Năm tương ứng với giá trị Số phép còn lại năm trước.",
    )

    def _get_leave_days_used_for_summary(self):
        """Tổng ngày nghỉ đã được phê duyệt (state = validate)."""
        self.ensure_one()
        groups = self.env["hr.leave"].sudo().read_group(
            domain=[
                ("employee_id", "=", self.id),
                ("state", "in", _LEAVES_DEDUCT_STATES),
            ],
            fields=["number_of_days:sum"],
            groupby=[],
        )
        if not groups:
            return 0.0
        row = groups[0]
        # Odoo 19 read_group tráº£ vá» key number_of_days (khÃ´ng cÃ²n number_of_days_sum).
        return row.get("number_of_days_sum") or row.get("number_of_days") or 0.0

    @api.depends("tong_so_phep")
    def _compute_time_off_summary(self):
        if "hr.leave.type" not in self.env:
            for employee in self:
                employee.da_su_dung = 0.0
                employee.con_lai = employee.tong_so_phep
            return
        for employee in self:
            # Chá»‰ Ä‘Æ¡n validate; khÃ´ng dÃ¹ng virtual_leaves_taken (Odoo cÃ³ thá»ƒ tÃ­nh cáº£ Ä‘Æ¡n chá» duyá»‡t).
            leave_taken = employee._get_leave_days_used_for_summary()
            employee.da_su_dung = leave_taken
            employee.con_lai = (employee.tong_so_phep or 0.0) - leave_taken

    @api.model
    def get_time_off_dashboard_data(self, target_date=None):
        """Làm mới số phép HRM trước khi dashboard đọc da_su_dung / con_lai."""
        employee = self._get_contextual_employee()
        ctx = {
            "employees_no_timeoff_write": True,
            "employees_no_allowed_employee_ids": [employee.id] if employee else [],
        }
        employee = employee.sudo().with_context(**ctx)
        if employee:
            employee._compute_time_off_summary()
        return super(HrEmployeeTimeoff, self.with_context(**ctx)).get_time_off_dashboard_data(
            target_date=target_date
        )

    @api.model
    def cron_snapshot_con_lai_prev_year(self):
        """Chạy vào 01/01 hàng năm: lưu con_lai của năm vừa kết thúc vào con_lai_nam_truoc.

        Không reset tong_so_phep hay da_su_dung — HR tự xử lý việc đó.
        """
        prev_year = date.today().year - 1
        employees = self.sudo().search([("active", "=", True)])
        if not employees:
            return

        # Refresh computed balances to make sure values reflect reality.
        employees._compute_time_off_summary()

        for emp in employees:
            emp.write({
                "con_lai_nam_truoc": emp.con_lai,
                "nam_chot_con_lai": prev_year,
            })
        _logger.info(
            "hr_employee_hrm_detail: snapshotted con_lai for %d employees (year=%d)",
            len(employees),
            prev_year,
        )


class HrLeaveTimeOffSummary(models.Model):
    _inherit = "hr.leave"

    @api.model
    def _con_lai_zero_no_confirmation(self):
        return {
            "needs_confirmation": False,
            "title": "",
            "message": "",
        }

    @api.model
    def _employee_id_from_preview_vals(self, vals, leave=None):
        val = (vals or {}).get("employee_id")
        if val in (False, None) and leave:
            return leave.employee_id.id
        if isinstance(val, models.Model):
            return val.id
        if isinstance(val, (list, tuple)) and val:
            return val[0]
        return val

    @api.model
    def check_con_lai_zero_confirmation(self, res_id=False, vals=None):
        """RPC cho UI: cáº£nh bÃ¡o khi cÃ²n láº¡i â‰¤ 0 trÆ°á»›c khi lÆ°u Ä‘Æ¡n (má»i loáº¡i nghá»‰)."""
        if self.env.context.get(_SKIP_CON_LAI_ZERO_CHECK_CTX) or self.env.context.get(
            _CON_LAI_ZERO_CONFIRMED_CTX
        ):
            return self._con_lai_zero_no_confirmation()

        vals = vals or {}
        leave = self.env["hr.leave"]
        if res_id:
            leave = self.browse(res_id).exists()
            if leave:
                leave.check_access("read")
        else:
            self.check_access("create")

        employee_id = self._employee_id_from_preview_vals(
            vals, leave if res_id and leave else None
        )
        if not employee_id:
            employee_id = self.env.user.employee_id.id
        if not employee_id:
            return self._con_lai_zero_no_confirmation()

        emp = self.env["hr.employee"].browse(employee_id)
        emp.with_context(
            employees_no_timeoff_write=True,
            employees_no_allowed_employee_ids=[employee_id],
        )._compute_time_off_summary()
        if (emp.con_lai or 0.0) > 0:
            return self._con_lai_zero_no_confirmation()

        return {
            "needs_confirmation": True,
            "title": _("Cảnh báo hết ngày phép"),
            "message": _("Bạn đang hết ngày phép, có chắc chắn muốn tiếp tục không?"),
        }

    def _recompute_employee_time_off_summary(self):
        employees = self.mapped("employee_id").filtered(lambda e: e.id)
        if employees:
            employees._compute_time_off_summary()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not self.env.context.get("leave_fast_create"):
            records._recompute_employee_time_off_summary()
        return records

    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get("leave_fast_create") and {
            "employee_id",
            "holiday_status_id",
            "number_of_days",
            "request_date_from",
            "request_date_to",
            "state",
        }.intersection(vals):
            self._recompute_employee_time_off_summary()
        return res

    def action_confirm(self):
        res = super().action_confirm()
        self._recompute_employee_time_off_summary()
        return res

    def action_validate(self):
        res = super().action_validate()
        self._recompute_employee_time_off_summary()
        return res

    def action_refuse(self):
        res = super().action_refuse()
        self._recompute_employee_time_off_summary()
        return res

    def action_draft(self):
        res = super().action_draft()
        self._recompute_employee_time_off_summary()
        return res
