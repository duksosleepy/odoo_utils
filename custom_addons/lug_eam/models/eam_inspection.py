# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class EamInspection(models.Model):
    _name = "eam.inspection"
    _description = "Phiếu kiểm tra tài sản"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        string="Số phiếu",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("New"),
    )
    asset_id = fields.Many2one(
        "maintenance.equipment",
        string="Tài sản",
        required=True,
        index=True,
    )
    date = fields.Date(
        string="Ngày kiểm tra",
        default=fields.Date.context_today,
        required=True,
    )
    inspector_id = fields.Many2one(
        "res.users",
        string="Người kiểm tra",
        default=lambda self: self.env.user,
    )
    state = fields.Selection(
        [
            ("draft", "Nháp"),
            ("done", "Hoàn thành"),
            ("cancel", "Hủy"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    result = fields.Selection(
        [
            ("pass", "Đạt"),
            ("fail", "Không đạt"),
        ],
        string="Kết luận",
    )
    line_ids = fields.One2many("eam.inspection.line", "inspection_id", string="Checklist")
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
    )
    note = fields.Text(string="Ghi chú")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") or vals.get("name") == _("New"):
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("eam.inspection") or _("New")
                )
        return super().create(vals_list)

    def action_complete(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("Cần ít nhất một mục kiểm tra."))
            fails = rec.line_ids.filtered(lambda l: l.result == "fail")
            rec.result = "fail" if fails else "pass"
            rec.state = "done"
            if rec.result == "fail":
                rec._create_corrective_request(fails)

    def _create_corrective_request(self, failed_lines):
        self.ensure_one()
        stage = self.env["maintenance.stage"].search([], order="sequence", limit=1)
        desc = "<br/>".join(
            failed_lines.mapped(lambda l: "%s: %s" % (l.criteria, l.note or ""))
        )
        self.env["maintenance.request"].create(
            {
                "name": _("Sửa chữa sau kiểm tra — %s") % self.asset_id.asset_code,
                "equipment_id": self.asset_id.id,
                "maintenance_type": "corrective",
                "description": desc,
                "stage_id": stage.id,
                "eam_work_type": _("Sửa chữa sau kiểm tra"),
            }
        )

    @api.model
    def _cron_eam_inspection_due(self):
        today = fields.Date.context_today(self)
        assets = self.env["maintenance.equipment"].search(
            [
                ("state", "in", ("in_stock", "in_use")),
                ("category_id.inspection_cycle_month", ">", 0),
            ]
        )
        for asset in assets:
            cycle = asset.category_id.inspection_cycle_month
            last = self.search(
                [("asset_id", "=", asset.id), ("state", "=", "done")],
                order="date desc",
                limit=1,
            )
            base = last.date if last else asset.purchase_date
            if not base:
                continue
            from dateutil.relativedelta import relativedelta

            due = base + relativedelta(months=cycle)
            if due > today:
                continue
            if self.search_count(
                [("asset_id", "=", asset.id), ("state", "=", "draft")]
            ):
                continue
            self.create(
                {
                    "asset_id": asset.id,
                    "date": today,
                    "line_ids": [
                        (0, 0, {"criteria": _("Kiểm tra tổng thể"), "sequence": 1}),
                        (0, 0, {"criteria": _("An toàn / vận hành"), "sequence": 2}),
                    ],
                }
            )


class EamInspectionLine(models.Model):
    _name = "eam.inspection.line"
    _description = "Dòng checklist kiểm tra"
    _order = "sequence, id"

    inspection_id = fields.Many2one(
        "eam.inspection",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(default=10)
    criteria = fields.Char(string="Tiêu chí", required=True)
    result = fields.Selection(
        [("pass", "Đạt"), ("fail", "Không đạt"), ("na", "N/A")],
        string="Kết quả",
    )
    note = fields.Char(string="Ghi chú")
