# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _

TXN_SEQ = {
    "in": "eam.txn.in",
    "out": "eam.txn.out",
    "transfer": "eam.txn.transfer",
    "count": "eam.txn.count",
    "disposal": "eam.txn.disposal",
}


class EamTransaction(models.Model):
    _name = "eam.transaction"
    _description = "Phiếu giao dịch tài sản"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        string="Số phiếu",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("New"),
        index=True,
    )
    txn_type = fields.Selection(
        [
            ("in", "Nhập kho"),
            ("out", "Xuất kho / Cấp phát"),
            ("transfer", "Điều chuyển"),
            ("count", "Kiểm kê"),
            ("disposal", "Thanh lý"),
        ],
        string="Loại phiếu",
        required=True,
        index=True,
        tracking=True,
    )
    state = fields.Selection(
        [
            ("draft", "Nháp"),
            ("to_approve", "Chờ duyệt"),
            ("done", "Hoàn thành"),
            ("cancel", "Hủy"),
        ],
        string="Trạng thái",
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    date = fields.Date(
        string="Ngày giao dịch",
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )
    warehouse_id = fields.Many2one("stock.warehouse", string="Kho", index=True)
    src_location_id = fields.Many2one("stock.location", string="Vị trí nguồn")
    dest_location_id = fields.Many2one("stock.location", string="Vị trí đích")
    department_id = fields.Many2one("hr.department", string="Phòng ban")
    owner_employee_id = fields.Many2one("hr.employee", string="Người nhận")
    partner_id = fields.Many2one("res.partner", string="Nhà cung cấp / Đối tác")
    reason = fields.Text(string="Lý do")
    amount_recovery = fields.Monetary(string="Giá trị thu hồi")
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Người tạo",
        default=lambda self: self.env.user,
        readonly=True,
    )
    approver_id = fields.Many2one("res.users", string="Người duyệt", readonly=True)
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )
    line_ids = fields.One2many("eam.transaction.line", "header_id", string="Chi tiết")
    line_count = fields.Integer(compute="_compute_line_count")

    _name_unique = models.Constraint("unique(name)", "Số phiếu phải là duy nhất.")

    @api.depends("line_ids")
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals.get("name") == _("New"):
                txn_type = vals.get("txn_type", "in")
                seq = TXN_SEQ.get(txn_type, "eam.txn.in")
                vals["name"] = self.env["ir.sequence"].next_by_code(seq) or _("New")
        return super().create(vals_list)

    def action_submit(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("Phiếu %s chưa có dòng tài sản.", rec.name))
            rec._validate_before_submit()
        self.write({"state": "to_approve"})

    def action_approve(self):
        for rec in self:
            if rec.state != "to_approve":
                raise UserError(_("Chỉ duyệt phiếu đang chờ duyệt."))
            rec._apply_lines()
        self.write({"state": "done", "approver_id": self.env.uid})

    def action_cancel(self):
        if any(rec.state == "done" for rec in self):
            raise UserError(_("Không hủy phiếu đã hoàn thành."))
        self.write({"state": "cancel"})

    def action_reset_draft(self):
        if any(rec.state == "done" for rec in self):
            raise UserError(_("Không đưa phiếu đã hoàn thành về nháp."))
        self.write({"state": "draft"})

    def _validate_before_submit(self):
        self.ensure_one()
        if self.txn_type == "out":
            for line in self.line_ids:
                if line.asset_id.state != "in_stock":
                    raise UserError(
                        _("Tài sản %s không ở trạng thái trong kho.")
                        % (line.asset_id.asset_code or line.asset_id.name)
                    )
            if not self.dest_location_id:
                raise UserError(_("Xuất kho cần vị trí sử dụng đích."))
            if not self.department_id and not self.owner_employee_id:
                raise UserError(_("Xuất kho cần phòng ban hoặc người nhận."))
        if self.txn_type == "in" and not self.dest_location_id:
            raise UserError(_("Nhập kho cần vị trí kho đích."))
        if self.txn_type in ("transfer", "out") and not self.dest_location_id:
            raise UserError(_("Cần chọn vị trí đích."))

    def _apply_lines(self):
        self.ensure_one()
        for line in self.line_ids:
            line._apply_to_asset(self)

    def action_load_expected_assets(self):
        """Kiểm kê: nạp danh sách tài sản kỳ vọng theo phạm vi."""
        self.ensure_one()
        if self.txn_type != "count":
            raise UserError(_("Chỉ dùng cho phiếu kiểm kê."))
        domain = [("state", "not in", ("disposed", "draft"))]
        if self.src_location_id:
            domain.append(("current_location_id", "child_of", self.src_location_id.id))
        elif self.warehouse_id:
            domain.append(("warehouse_id", "=", self.warehouse_id.id))
        assets = self.env["maintenance.equipment"].search(domain)
        existing = set(self.line_ids.mapped("asset_id").ids)
        lines = []
        for asset in assets:
            if asset.id in existing:
                continue
            lines.append(
                {
                    "header_id": self.id,
                    "asset_id": asset.id,
                    "from_location_id": asset.current_location_id.id,
                    "from_state": asset.state,
                    "counted": False,
                }
            )
        if lines:
            self.env["eam.transaction.line"].create(lines)
        return True


class EamTransactionLine(models.Model):
    _name = "eam.transaction.line"
    _description = "Chi tiết phiếu giao dịch tài sản"
    _order = "id"

    header_id = fields.Many2one(
        "eam.transaction",
        required=True,
        ondelete="cascade",
        index=True,
    )
    txn_type = fields.Selection(related="header_id.txn_type", store=True)
    asset_id = fields.Many2one(
        "maintenance.equipment",
        string="Tài sản",
        required=True,
        index=True,
    )
    asset_code = fields.Char(related="asset_id.asset_code", store=True)
    from_location_id = fields.Many2one("stock.location", string="Vị trí trước")
    to_location_id = fields.Many2one("stock.location", string="Vị trí sau")
    from_state = fields.Char(string="Trạng thái trước")
    to_state = fields.Char(string="Trạng thái sau")
    counted = fields.Boolean(string="Đã quét")
    discrepancy = fields.Selection(
        [
            ("ok", "Khớp"),
            ("missing", "Thiếu"),
            ("surplus", "Thừa"),
            ("wrong_location", "Sai vị trí"),
        ],
        string="Chênh lệch",
    )
    note = fields.Text(string="Ghi chú")

    _header_asset_unique = models.Constraint(
        "unique(header_id, asset_id)",
        "Mỗi tài sản chỉ xuất hiện một lần trên phiếu.",
    )

    @api.constrains("asset_id", "header_id")
    def _check_asset_not_disposed(self):
        for line in self:
            if line.asset_id.state == "disposed" and line.header_id.txn_type != "disposal":
                raise ValidationError(
                    _("Tài sản %s đã thanh lý.") % line.asset_id.asset_code
                )

    def _apply_to_asset(self, header):
        self.ensure_one()
        asset = self.asset_id
        vals = {}
        loc = header.dest_location_id

        if header.txn_type == "in":
            asset._set_state("in_stock")
            vals.update(
                {
                    "current_location_id": loc.id,
                    "warehouse_id": header.warehouse_id.id or loc.warehouse_id.id,
                    "department_id": False,
                    "owner_employee_id": False,
                }
            )
        elif header.txn_type == "out":
            asset._set_state("in_use")
            vals.update(
                {
                    "current_location_id": loc.id,
                    "department_id": header.department_id.id,
                    "owner_employee_id": header.owner_employee_id.id,
                    "assign_date": header.date,
                    "warehouse_id": False,
                }
            )
        elif header.txn_type == "transfer":
            if loc and loc._eam_is_warehouse_kind():
                asset._set_state("in_stock")
                vals.update(
                    {
                        "current_location_id": loc.id,
                        "warehouse_id": header.warehouse_id.id or loc.warehouse_id.id,
                        "department_id": False,
                        "owner_employee_id": False,
                    }
                )
            else:
                asset._set_state("in_use")
                vals.update(
                    {
                        "current_location_id": loc.id,
                        "department_id": header.department_id.id or asset.department_id.id,
                        "owner_employee_id": header.owner_employee_id.id
                        or asset.owner_employee_id.id,
                    }
                )
        elif header.txn_type == "count":
            if self.discrepancy == "wrong_location" and loc:
                vals["current_location_id"] = loc.id
            elif self.discrepancy == "ok" and self.counted:
                pass
        elif header.txn_type == "disposal":
            if asset.maintenance_ids.filtered(lambda m: not m.stage_id.done):
                raise UserError(
                    _("Tài sản %s còn phiếu bảo trì mở.") % asset.asset_code
                )
            asset._set_state("disposed")
            vals["scrap_date"] = header.date

        self.from_location_id = asset.current_location_id
        self.from_state = asset.state
        if vals:
            asset.write(vals)
        self.to_location_id = asset.current_location_id
        self.to_state = asset.state
        asset._eam_log_transaction(header, self)
