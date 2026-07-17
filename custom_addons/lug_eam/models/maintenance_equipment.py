# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _

# State machine hợp lệ (xem 05_Workflow.md)
EAM_TRANSITIONS = {
    "draft": {"in_stock"},
    "in_stock": {"in_use", "maintenance", "broken", "disposed"},
    "in_use": {"in_stock", "maintenance", "broken", "disposed"},
    "maintenance": {"in_stock", "in_use", "broken", "disposed"},
    "broken": {"in_stock", "maintenance", "disposed"},
    "disposed": set(),
}


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    asset_code = fields.Char(
        string="Mã tài sản",
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _("New"),
    )
    eam_model_id = fields.Many2one("eam.model", string="Model", index=True)
    eam_brand_id = fields.Many2one(
        "eam.brand",
        string="Thương hiệu",
        related="eam_model_id.brand_id",
        store=True,
        readonly=True,
    )
    state = fields.Selection(
        [
            ("draft", "Nháp"),
            ("in_stock", "Trong kho"),
            ("in_use", "Đang sử dụng"),
            ("maintenance", "Đang bảo trì"),
            ("broken", "Hỏng"),
            ("disposed", "Đã thanh lý"),
        ],
        string="Trạng thái",
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    warehouse_id = fields.Many2one("stock.warehouse", string="Kho")
    current_location_id = fields.Many2one(
        "stock.location", string="Vị trí hiện tại", tracking=True
    )
    department_id = fields.Many2one("hr.department", string="Phòng ban")
    owner_employee_id = fields.Many2one("hr.employee", string="Người giữ")
    purchase_date = fields.Date(string="Ngày mua")
    currency_id = fields.Many2one(
        "res.currency",
        string="Tiền tệ",
        default=lambda self: self.env.company.currency_id,
    )
    po_ref = fields.Char(string="Số PO / Hóa đơn")
    funding_source = fields.Char(string="Nguồn vốn")
    warranty_start = fields.Date(string="Bắt đầu bảo hành")
    warranty_state = fields.Selection(
        [
            ("none", "Không có"),
            ("valid", "Còn hạn"),
            ("expiring", "Sắp hết"),
            ("expired", "Hết hạn"),
        ],
        string="Tình trạng bảo hành",
        compute="_compute_warranty_state",
        store=True,
    )
    qr_code = fields.Char(string="Mã QR", copy=False, readonly=True, index=True)
    image_1920 = fields.Image(string="Hình ảnh", max_width=1920, max_height=1920)
    next_maintenance_date = fields.Date(
        string="Bảo trì kế tiếp", compute="_compute_next_maintenance_date", store=True
    )
    eam_loc_kind = fields.Selection(
        related="current_location_id.eam_loc_kind",
        string="Loại vị trí",
        store=True,
        readonly=True,
    )
    transaction_ids = fields.One2many(
        "eam.transaction.line",
        "asset_id",
        string="Giao dịch",
    )
    transaction_count = fields.Integer(compute="_compute_transaction_count")
    eam_maintenance_cost = fields.Monetary(
        string="Chi phí bảo trì lũy kế",
        compute="_compute_eam_maintenance_cost",
        store=True,
        groups="lug_eam.group_eam_asset_manager,lug_eam.group_eam_maint_manager,lug_eam.group_eam_admin",
    )

    _asset_code_unique = models.Constraint(
        "unique(asset_code)", "Mã tài sản phải là duy nhất."
    )

    @api.depends("transaction_ids")
    def _compute_transaction_count(self):
        for rec in self:
            rec.transaction_count = len(rec.transaction_ids)

    @api.depends("maintenance_ids.eam_total_cost", "maintenance_ids.stage_id.done")
    def _compute_eam_maintenance_cost(self):
        for rec in self:
            done_reqs = rec.maintenance_ids.filtered(lambda r: r.stage_id.done)
            rec.eam_maintenance_cost = sum(done_reqs.mapped("eam_total_cost"))

    @api.constrains("serial_no")
    def _check_serial_no_unique(self):
        """BR001 — Serial Number không được trùng (bỏ qua giá trị rỗng)."""
        for rec in self:
            if not rec.serial_no:
                continue
            duplicate = self.search_count(
                [("serial_no", "=", rec.serial_no), ("id", "!=", rec.id)]
            )
            if duplicate:
                raise ValidationError(
                    _(
                        "Serial Number '%s' đã tồn tại ở tài sản khác.",
                        rec.serial_no,
                    )
                )

    @api.constrains("state", "current_location_id", "department_id", "owner_employee_id")
    def _check_location_and_owner_rules(self):
        for rec in self:
            loc = rec.current_location_id
            if rec.state == "in_stock" and loc and not loc._eam_is_warehouse_kind():
                raise ValidationError(
                    _("Tài sản trong kho phải ở vị trí loại kho.")
                )
            if rec.state == "in_use":
                if loc and not loc._eam_is_usage_kind():
                    raise ValidationError(
                        _("Tài sản đang sử dụng phải ở vị trí sử dụng.")
                    )
                if not rec.department_id and not rec.owner_employee_id:
                    raise ValidationError(
                        _("Tài sản đang sử dụng cần phòng ban hoặc người giữ.")
                    )
            if rec.category_id and rec.category_id.require_warranty:
                if not rec.warranty_date and rec.state not in ("draft", "disposed"):
                    raise ValidationError(
                        _("Nhóm %s bắt buộc nhập bảo hành.")
                        % rec.category_id.name
                    )

    @api.constrains("eam_model_id")
    def _check_eam_model_required(self):
        for rec in self:
            if rec.state != "draft" and not rec.eam_model_id:
                raise ValidationError(_("Tài sản cần chọn Model (chủng loại)."))

    @api.depends("warranty_date")
    def _compute_warranty_state(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if not rec.warranty_date:
                rec.warranty_state = "none"
            elif rec.warranty_date < today:
                rec.warranty_state = "expired"
            elif rec.warranty_date <= today + relativedelta(days=30):
                rec.warranty_state = "expiring"
            else:
                rec.warranty_state = "valid"

    @api.ondelete(at_uninstall=False)
    def _unlink_check_eam(self):
        for rec in self:
            if rec.transaction_ids or rec.maintenance_ids:
                raise UserError(
                    _("Không xóa tài sản đã phát sinh giao dịch hoặc bảo trì.")
                )

    @api.depends("purchase_date", "effective_date", "category_id.maintenance_cycle_month")
    def _compute_next_maintenance_date(self):
        for rec in self:
            cycle = rec.category_id.maintenance_cycle_month or 0
            base = rec.purchase_date or rec.effective_date
            if cycle and base:
                rec.next_maintenance_date = base + relativedelta(months=cycle)
            else:
                rec.next_maintenance_date = False

    @api.onchange("eam_model_id")
    def _onchange_eam_model_id(self):
        if self.eam_model_id:
            self.category_id = self.eam_model_id.category_id
            if self.eam_model_id.default_warranty_month and self.purchase_date:
                self.warranty_date = self.purchase_date + relativedelta(
                    months=self.eam_model_id.default_warranty_month
                )

    # Field → (event_type, label) để ghi lịch sử tài sản
    _EAM_HISTORY_TRACKED = {
        "state": ("state", "Trạng thái"),
        "current_location_id": ("location", "Vị trí"),
        "owner_employee_id": ("owner", "Người giữ"),
    }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("asset_code") or vals.get("asset_code") == _("New"):
                vals["asset_code"] = self.env["ir.sequence"].next_by_code(
                    "eam.asset"
                ) or _("New")
            # đồng bộ category từ model nếu chưa có
            if vals.get("eam_model_id") and not vals.get("category_id"):
                model = self.env["eam.model"].browse(vals["eam_model_id"])
                vals["category_id"] = model.category_id.id
        records = super().create(vals_list)
        history_vals = []
        for rec in records:
            rec._assign_qr_code()
            history_vals.append({
                "asset_id": rec.id,
                "event_type": "create",
                "new_value": rec.asset_code or rec.name,
                "note": "Tạo mới tài sản",
            })
        if history_vals:
            self.env["eam.asset.history"].sudo().create(history_vals)
        return records

    def write(self, vals):
        tracked = self._EAM_HISTORY_TRACKED
        old_values = {}
        if any(field in vals for field in tracked):
            old_values = {
                rec.id: {
                    field: rec._eam_history_value(field)
                    for field in tracked
                    if field in vals
                }
                for rec in self
            }
        res = super().write(vals)
        if "eam_model_id" in vals:
            for rec in self:
                if rec.eam_model_id and not rec.category_id:
                    rec.category_id = rec.eam_model_id.category_id
        if old_values:
            self._eam_log_history(old_values)
        return res

    def _eam_history_value(self, field):
        """Chuỗi hiển thị cho giá trị của field (dùng cho lịch sử)."""
        self.ensure_one()
        if field == "state":
            return dict(self._fields["state"].selection).get(self.state) or ""
        value = self[field]
        return value.display_name if value else ""

    def _eam_log_history(self, old_values):
        history_vals = []
        for rec in self:
            snapshot = old_values.get(rec.id, {})
            for field, (event_type, label) in self._EAM_HISTORY_TRACKED.items():
                if field not in snapshot:
                    continue
                old_display = snapshot[field]
                new_display = rec._eam_history_value(field)
                if old_display == new_display:
                    continue
                history_vals.append({
                    "asset_id": rec.id,
                    "event_type": event_type,
                    "old_value": old_display,
                    "new_value": new_display,
                    "note": "%s: %s → %s" % (
                        label, old_display or "—", new_display or "—"
                    ),
                })
        if history_vals:
            self.env["eam.asset.history"].sudo().create(history_vals)

    def _assign_qr_code(self):
        for rec in self:
            if not rec.qr_code and rec.asset_code and rec.asset_code != _("New"):
                if not rec.category_id or rec.category_id.require_qr:
                    rec.qr_code = rec.asset_code

    def _set_state(self, new_state):
        for rec in self:
            allowed = EAM_TRANSITIONS.get(rec.state, set())
            if new_state != rec.state and new_state not in allowed:
                raise UserError(
                    _(
                        "Không thể chuyển tài sản %(code)s từ '%(a)s' sang '%(b)s'.",
                        code=rec.asset_code or rec.name,
                        a=dict(self._fields["state"].selection).get(rec.state),
                        b=dict(self._fields["state"].selection).get(new_state),
                    )
                )
            rec.state = new_state

    def action_set_in_stock(self):
        self._set_state("in_stock")

    def action_set_in_use(self):
        self._set_state("in_use")

    def action_set_maintenance(self):
        self._set_state("maintenance")

    def action_report_broken(self):
        self._set_state("broken")

    def action_dispose(self):
        for rec in self:
            if rec.maintenance_ids.filtered(lambda m: not m.stage_id.done):
                raise UserError(
                    _(
                        "Không thể thanh lý tài sản %s khi còn phiếu bảo trì chưa đóng.",
                        rec.asset_code or rec.name,
                    )
                )
        self._set_state("disposed")
        self.write({"scrap_date": fields.Date.context_today(self)})

    def _eam_log_transaction(self, header, line):
        self.ensure_one()
        type_label = dict(header._fields["txn_type"].selection).get(header.txn_type)
        self.env["eam.asset.history"].sudo().create(
            {
                "asset_id": self.id,
                "event_type": "transaction",
                "old_value": line.from_state or "",
                "new_value": line.to_state or "",
                "note": "%s — %s" % (type_label, header.name),
            }
        )

    def action_view_transactions(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Giao dịch"),
            "res_model": "eam.transaction.line",
            "view_mode": "list,form",
            "domain": [("asset_id", "=", self.id)],
            "context": {"default_asset_id": self.id},
        }

    def action_view_maintenance(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Bảo trì"),
            "res_model": "maintenance.request",
            "view_mode": "kanban,list,form",
            "domain": [("equipment_id", "=", self.id)],
            "context": {"default_equipment_id": self.id},
        }

    def action_create_corrective_request(self):
        self.ensure_one()
        stage = self.env["maintenance.stage"].search([], order="sequence", limit=1)
        sla_hours = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("lug_eam.sla_hours", "48")
        )
        from datetime import timedelta

        return {
            "type": "ir.actions.act_window",
            "name": _("Phiếu bảo trì"),
            "res_model": "maintenance.request",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_equipment_id": self.id,
                "default_maintenance_type": "corrective",
                "default_name": _("Báo hỏng — %s") % (self.asset_code or self.name),
                "default_stage_id": stage.id,
                "default_sla_deadline": fields.Datetime.now()
                + timedelta(hours=sla_hours),
            },
        }

    @api.model
    def _cron_eam_warranty_alert(self):
        days = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("lug_eam.warranty_alert_days", "30")
        )
        today = fields.Date.context_today(self)
        limit = today + relativedelta(days=days)
        assets = self.search(
            [
                ("warranty_date", "!=", False),
                ("warranty_date", "<=", limit),
                ("warranty_date", ">=", today),
                ("state", "not in", ("disposed", "draft")),
            ]
        )
        managers = self.env.ref("lug_eam.group_eam_asset_manager").users
        for asset in assets:
            for user in managers:
                asset.activity_schedule(
                    "mail.mail_activity_data_todo",
                    summary=_("Bảo hành sắp hết — %s") % asset.asset_code,
                    user_id=user.id,
                )
