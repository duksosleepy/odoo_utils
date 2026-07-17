# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

TASK_STATES = [
    ("draft", "Nháp"),
    ("approved", "Đã duyệt"),
    ("assigned", "Đã giao"),
    ("accepted", "Đã nhận"),
    ("in_progress", "Đang làm"),
    ("pending", "Tạm dừng"),
    ("review", "Chờ duyệt kết quả"),
    ("completed", "Hoàn thành"),
    ("closed", "Đóng"),
    ("overdue", "Quá hạn"),
    ("escalation", "Leo thang"),
]

ASSIGNMENT_LEVEL = {
    "giám đốc": 1,
    "admin tổng": 1,
    "rsm": 2,
    "asm": 2,
    "trưởng phòng": 3,
    "trưởng phòng hcns": 3,
    "trưởng bộ phận": 3,
    "cửa hàng trưởng": 3,
    "trưởng nhóm": 4,
    "nhóm trưởng": 4,
    "giám sát": 4,
    "quản lý kho": 4,
    "nhân viên vp": 5,
    "nhân viên ch": 5,
    "admin": 5,
}


class LugTask(models.Model):
    _name = "lug.task"
    _description = "Công việc giao việc IT"
    _inherit = ["mail.thread", "mail.activity.mixin", "lug.task.notify.mixin"]
    _order = "priority_id, due_date, id desc"
    _rec_name = "title"

    task_code = fields.Char(
        string="Mã việc",
        copy=False,
        readonly=True,
        index=True,
        default="/",
    )
    parent_task_id = fields.Many2one(
        "lug.task",
        string="Việc cha",
        ondelete="set null",
        index=True,
    )
    child_task_ids = fields.One2many("lug.task", "parent_task_id", string="Việc con")
    title = fields.Char(string="Tiêu đề", required=True, tracking=True)
    description = fields.Html(string="Mô tả")
    category_id = fields.Many2one(
        "lug.task.category",
        string="Loại việc",
        required=True,
        tracking=True,
    )
    priority_id = fields.Many2one(
        "lug.task.priority",
        string="Mức độ",
        required=True,
        tracking=True,
    )
    point = fields.Float(
        string="Điểm",
        compute="_compute_point",
        store=True,
        readonly=False,
        tracking=True,
    )
    assigned_by_id = fields.Many2one(
        "hr.employee",
        string="Người giao",
        tracking=True,
        index=True,
        default=lambda self: self.env.user.sudo().employee_id,
    )
    assigned_to_id = fields.Many2one(
        "hr.employee",
        string="Người nhận",
        tracking=True,
        index=True,
    )
    reviewer_id = fields.Many2one("hr.employee", string="Người duyệt kết quả")
    approver_id = fields.Many2one("hr.employee", string="Người phê duyệt")
    approval_date = fields.Datetime(string="Ngày phê duyệt", readonly=True)
    review_date = fields.Datetime(string="Ngày duyệt kết quả", readonly=True)
    rejection_reason = fields.Text(string="Lý do từ chối")
    department_id = fields.Many2one(
        "hr.department",
        string="Phòng ban",
        index=True,
    )
    mien_zone_id = fields.Many2one(
        "hr.mien.zone",
        string="Miền",
        index=True,
    )
    store_id = fields.Many2one(
        "hr.store",
        string="Chi nhánh / Cửa hàng",
        index=True,
    )
    start_date = fields.Datetime(string="Ngày bắt đầu", tracking=True)
    due_date = fields.Datetime(string="Hạn hoàn thành", tracking=True)
    sla_deadline = fields.Datetime(
        string="Hạn SLA",
        compute="_compute_sla_deadline",
        store=True,
    )
    completed_date = fields.Datetime(string="Ngày hoàn thành", readonly=True)
    state = fields.Selection(
        selection=TASK_STATES,
        string="Trạng thái",
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    progress = fields.Integer(string="Tiến độ (%)", default=0)
    estimate_hours = fields.Float(string="Giờ ước tính")
    actual_hours = fields.Float(
        string="Giờ thực tế",
        compute="_compute_actual_hours",
        store=True,
    )
    is_overdue = fields.Boolean(compute="_compute_is_overdue", store=True)
    is_quality_issue = fields.Boolean(
        string="Lỗi chất lượng",
        help="Đánh dấu khi công việc có lỗi sau khi review.",
    )
    process_compliant = fields.Boolean(
        string="Đúng quy trình",
        default=True,
        help="Bỏ chọn nếu nhân viên không cập nhật đúng quy trình.",
    )
    sla_alert_24h_sent = fields.Boolean(default=False, copy=False)
    sla_alert_4h_sent = fields.Boolean(default=False, copy=False)
    company_id = fields.Many2one(
        "res.company",
        string="Công ty",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    comment_ids = fields.One2many("lug.task.comment", "task_id", string="Bình luận")
    checklist_ids = fields.One2many("lug.task.checklist", "task_id", string="Checklist")
    timesheet_ids = fields.One2many("lug.task.timesheet", "task_id", string="Timesheet")
    history_ids = fields.One2many("lug.task.history", "task_id", string="Lịch sử")
    attachment_count = fields.Integer(compute="_compute_attachment_count")
    checklist_progress = fields.Integer(compute="_compute_checklist_progress")

    @api.depends("category_id", "category_id.point")
    def _compute_point(self):
        for task in self:
            task.point = task.category_id.point if task.category_id else 0.0

    @api.depends("timesheet_ids.hours")
    def _compute_actual_hours(self):
        for task in self:
            task.actual_hours = sum(task.timesheet_ids.mapped("hours"))

    @api.depends("checklist_ids.completed")
    def _compute_checklist_progress(self):
        for task in self:
            items = task.checklist_ids
            if not items:
                task.checklist_progress = task.progress
            else:
                done = len(items.filtered("completed"))
                task.checklist_progress = int(done * 100 / len(items))

    @api.depends("start_date", "priority_id.sla_hours", "due_date")
    def _compute_sla_deadline(self):
        for task in self:
            base = task.start_date or fields.Datetime.now()
            if task.priority_id and task.priority_id.sla_hours:
                task.sla_deadline = base + timedelta(hours=task.priority_id.sla_hours)
            else:
                task.sla_deadline = task.due_date

    @api.depends("due_date", "state", "completed_date")
    def _compute_is_overdue(self):
        now = fields.Datetime.now()
        for task in self:
            if task.state in ("closed", "completed"):
                task.is_overdue = bool(
                    task.due_date
                    and task.completed_date
                    and task.completed_date > task.due_date
                )
            elif task.due_date and task.state not in ("closed",):
                task.is_overdue = task.due_date < now
            else:
                task.is_overdue = False

    def _compute_attachment_count(self):
        Attachment = self.env["ir.attachment"]
        for task in self:
            task.attachment_count = Attachment.search_count(
                [
                    ("res_model", "=", self._name),
                    ("res_id", "=", task.id),
                ]
            )

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        employee = self.env.user.sudo().employee_id
        if employee and "assigned_by_id" in fields_list and not vals.get("assigned_by_id"):
            vals["assigned_by_id"] = employee.id
        if employee and "approver_id" in fields_list and not vals.get("approver_id"):
            vals["approver_id"] = employee.parent_id.id if employee.parent_id else employee.id
        if employee and "reviewer_id" in fields_list and not vals.get("reviewer_id"):
            vals["reviewer_id"] = employee.parent_id.id if employee.parent_id else False
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("task_code", "/") == "/":
                vals["task_code"] = self.env["ir.sequence"].next_by_code("lug.task") or "/"
            if not vals.get("assigned_by_id"):
                employee = self.env.user.sudo().employee_id
                if employee:
                    vals["assigned_by_id"] = employee.id
            self._prepare_org_snapshot(vals)
        records = super().create(vals_list)
        for record in records:
            record._log_history("create", False, record.display_name)
        return records

    def write(self, vals):
        tracked = {f for f in ("state", "assigned_to_id", "progress", "due_date") if f in vals}
        old = {rec.id: {f: rec[f] for f in tracked} for rec in self} if tracked else {}
        if any(k in vals for k in ("assigned_to_id", "department_id", "mien_zone_id", "store_id")):
            self._prepare_org_snapshot(vals)
        if "due_date" in vals:
            vals["sla_alert_24h_sent"] = False
            vals["sla_alert_4h_sent"] = False
        res = super().write(vals)
        for rec in self:
            for field_name in tracked:
                rec._log_history(field_name, old.get(rec.id, {}).get(field_name), rec[field_name])
        return res

    @api.model
    def _prepare_org_snapshot(self, vals):
        employee_id = vals.get("assigned_to_id")
        if not employee_id:
            return
        employee = self.env["hr.employee"].sudo().browse(employee_id)
        if not employee.exists():
            return
        if "department_id" not in vals and employee.department_id:
            vals["department_id"] = employee.department_id.id
        if "mien_zone_id" not in vals and employee.mien_zone_id:
            vals["mien_zone_id"] = employee.mien_zone_id.id
        if "store_id" not in vals and employee.ma_bo_phan_id:
            vals["store_id"] = employee.ma_bo_phan_id.store_id.id

    @api.model
    def _employee_assignment_level(self, employee):
        if not employee:
            return 99
        title = (employee.job_title or "").strip().lower()
        return ASSIGNMENT_LEVEL.get(title, 5)

    def _check_assignment_hierarchy(self, assigner, assignee):
        if not assigner or not assignee:
            return
        assigner_level = self._employee_assignment_level(assigner)
        assignee_level = self._employee_assignment_level(assignee)
        if self.env.user.has_group("lug_task_assignment.group_lug_task_admin"):
            return
        if assigner_level >= assignee_level:
            raise ValidationError(
                "Không được giao việc vượt cấp hoặc ngang cấp. "
                "Chỉ giao cho cấp dưới trực tiếp theo sơ đồ tổ chức."
            )
        if assignee_level - assigner_level > 1:
            raise ValidationError(
                "Không được giao việc nhảy cấp. "
                "Vui lòng giao qua cấp quản lý trung gian."
            )

    @api.constrains("assigned_by_id", "assigned_to_id")
    def _constrain_assignment_hierarchy(self):
        for task in self:
            if task.assigned_by_id and task.assigned_to_id:
                task._check_assignment_hierarchy(task.assigned_by_id, task.assigned_to_id)

    def _log_history(self, action, old_value, new_value):
        self.ensure_one()
        self.env["lug.task.history"].sudo().create(
            {
                "task_id": self.id,
                "action": action,
                "old_value": str(old_value) if old_value is not False else "",
                "new_value": str(new_value) if new_value is not False else "",
                "created_by_id": self.env.user.id,
            }
        )

    def _check_approver(self):
        self.ensure_one()
        approver = self.approver_id
        current = self.env.user.sudo().employee_id
        if self.env.user.has_group("lug_task_assignment.group_lug_task_admin"):
            return
        if approver and current and approver.id != current.id:
            raise UserError("Chỉ người phê duyệt được duyệt công việc này.")

    def _check_reviewer(self):
        self.ensure_one()
        reviewer = self.reviewer_id
        current = self.env.user.sudo().employee_id
        if self.env.user.has_group("lug_task_assignment.group_lug_task_manager"):
            return
        if reviewer and current and reviewer.id != current.id:
            raise UserError("Chỉ người duyệt kết quả được xác nhận.")

    def action_submit_for_approval(self):
        for task in self:
            if not task.approver_id:
                raise UserError("Chọn người phê duyệt trước.")
        self._set_state("draft")
        for task in self:
            if task.approver_id and task.approver_id.user_id:
                task.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=task.approver_id.user_id.id,
                    summary="Phê duyệt giao việc: %s" % task.title,
                )

    def action_approve(self):
        for task in self:
            task._check_approver()
        self.write({"state": "approved", "approval_date": fields.Datetime.now()})

    def action_assign(self):
        for task in self:
            if not task.assigned_to_id:
                raise UserError("Chọn người nhận việc trước khi giao.")
            if task.state == "draft":
                raise UserError("Duyệt công việc trước khi giao.")
            assigner = task.assigned_by_id or self.env.user.sudo().employee_id
            task._check_assignment_hierarchy(assigner, task.assigned_to_id)
        self._set_state("assigned")
        for task in self:
            task._lug_task_notify_assignment(task)

    def action_accept(self):
        for task in self:
            assignee = task.assigned_to_id
            current = self.env.user.sudo().employee_id
            if (
                assignee
                and current
                and assignee.id != current.id
                and not self.env.user.has_group("lug_task_assignment.group_lug_task_admin")
            ):
                raise UserError("Chỉ người được giao mới nhận việc.")
        self._set_state("accepted")

    def action_start(self):
        self.write({"state": "in_progress", "start_date": fields.Datetime.now()})

    def action_pending(self):
        self._set_state("pending")

    def action_submit_review(self):
        for task in self:
            if task.checklist_ids and not all(task.checklist_ids.mapped("completed")):
                raise UserError("Hoàn thành checklist trước khi gửi duyệt.")
        self._set_state("review")
        for task in self:
            task._lug_task_notify_review_request(task)

    def action_complete(self):
        for task in self:
            task._check_reviewer()
            if task.is_quality_issue:
                task._log_history("quality_issue", False, True)
        self.write(
            {
                "state": "completed",
                "completed_date": fields.Datetime.now(),
                "review_date": fields.Datetime.now(),
                "progress": 100,
            }
        )

    def action_reject_review(self):
        for task in self:
            task._check_reviewer()
            if not task.rejection_reason:
                raise UserError("Nhập lý do từ chối.")
            task.is_quality_issue = True
        self.write({"state": "in_progress"})

    def action_close(self):
        if not self.env.user.has_group("lug_task_assignment.group_lug_task_manager"):
            raise UserError("Chỉ Trưởng phòng trở lên được đóng việc.")
        self._set_state("closed")

    def _set_state(self, new_state):
        self.write({"state": new_state})

    @api.model
    def _cron_sla_alerts(self):
        now = fields.Datetime.now()
        tasks = self.search(
            [
                ("state", "not in", ("closed", "completed", "overdue", "escalation")),
                ("due_date", "!=", False),
            ]
        )
        for task in tasks:
            if not task.due_date:
                continue
            hours_left = (task.due_date - now).total_seconds() / 3600.0
            if hours_left <= 0:
                task._handle_overdue()
            elif hours_left <= 4 and not task.sla_alert_4h_sent:
                task._notify_manager_sla(hours_left)
                task.sla_alert_4h_sent = True
            elif hours_left <= 24 and not task.sla_alert_24h_sent:
                task._notify_assignee_sla(hours_left)
                task.sla_alert_24h_sent = True

    def _handle_overdue(self):
        self.ensure_one()
        if self.state in ("overdue", "escalation", "closed"):
            return
        self.write({"state": "overdue"})
        self._notify_overdue_escalation()
        self._lug_task_notify_overdue(self)

    def _notify_assignee_sla(self, hours_left):
        self.ensure_one()
        self.message_post(
            body="Còn %.0f giờ đến hạn hoàn thành." % hours_left,
            partner_ids=self.assigned_to_id.user_id.partner_id.ids if self.assigned_to_id.user_id else [],
            subtype_xmlid="mail.mt_note",
        )

    def _notify_manager_sla(self, hours_left):
        self.ensure_one()
        manager = self.assigned_to_id.parent_id if self.assigned_to_id else False
        partners = manager.user_id.partner_id.ids if manager and manager.user_id else []
        self.message_post(
            body="Việc sắp quá hạn (còn %.0f giờ)." % hours_left,
            partner_ids=partners,
            subtype_xmlid="mail.mt_note",
        )

    def _notify_overdue_escalation(self):
        self.ensure_one()
        self.write({"state": "escalation"})
        partners = []
        if self.assigned_to_id and self.assigned_to_id.parent_id and self.assigned_to_id.parent_id.user_id:
            partners.append(self.assigned_to_id.parent_id.user_id.partner_id.id)
        dept_manager = self.department_id.manager_id if self.department_id else False
        if dept_manager and dept_manager.user_id:
            partners.append(dept_manager.user_id.partner_id.id)
        self.message_post(
            body="Công việc đã quá hạn — đã leo thang và thông báo quản lý.",
            partner_ids=list(set(partners)),
            subtype_xmlid="mail.mt_comment",
        )

    def action_open_attachments(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Tệp đính kèm",
            "res_model": "ir.attachment",
            "view_mode": "list,form",
            "domain": [("res_model", "=", self._name), ("res_id", "=", self.id)],
            "context": {
                "default_res_model": self._name,
                "default_res_id": self.id,
            },
        }
