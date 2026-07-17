# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    eam_labor_cost = fields.Monetary(string="Chi phí nhân công")
    eam_part_cost = fields.Monetary(
        string="Chi phí linh kiện",
        compute="_compute_eam_part_cost",
        store=True,
    )
    eam_total_cost = fields.Monetary(
        string="Tổng chi phí",
        compute="_compute_eam_total_cost",
        store=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
    )
    part_ids = fields.One2many("eam.maintenance.part", "request_id", string="Linh kiện")
    sla_deadline = fields.Datetime(string="Hạn SLA")
    sla_state = fields.Selection(
        [
            ("none", "Không áp dụng"),
            ("ok", "Trong hạn"),
            ("breach", "Quá hạn"),
        ],
        string="Tình trạng SLA",
        compute="_compute_sla_state",
        store=True,
    )
    eam_work_type = fields.Char(string="Loại công việc")

    @api.depends("part_ids.subtotal")
    def _compute_eam_part_cost(self):
        for rec in self:
            rec.eam_part_cost = sum(rec.part_ids.mapped("subtotal"))

    @api.depends("eam_labor_cost", "eam_part_cost")
    def _compute_eam_total_cost(self):
        for rec in self:
            rec.eam_total_cost = (rec.eam_labor_cost or 0.0) + (rec.eam_part_cost or 0.0)

    @api.depends("sla_deadline", "stage_id.done", "close_date")
    def _compute_sla_state(self):
        now = fields.Datetime.now()
        for rec in self:
            if not rec.sla_deadline:
                rec.sla_state = "none"
            elif rec.stage_id.done:
                end = rec.close_date or fields.Date.context_today(rec)
                deadline = fields.Datetime.to_datetime(rec.sla_deadline)
                rec.sla_state = "ok" if end <= deadline.date() else "breach"
            else:
                rec.sla_state = "breach" if now > rec.sla_deadline else "ok"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("equipment_id") and not vals.get("sla_deadline"):
                equip = self.env["maintenance.equipment"].browse(vals["equipment_id"])
                if equip and equip.state not in ("maintenance", "broken"):
                    equip._set_state("maintenance")
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        if "stage_id" in vals:
            for rec in self:
                if rec.stage_id.done and rec.equipment_id:
                    if rec.equipment_id.state == "maintenance":
                        rec.equipment_id._set_state("in_use")
        return res

    @api.model
    def _cron_eam_preventive_maintenance(self):
        """Sinh phiếu bảo trì phòng ngừa theo chu kỳ Category."""
        today = fields.Date.context_today(self)
        assets = self.env["maintenance.equipment"].search(
            [
                ("state", "in", ("in_stock", "in_use")),
                ("category_id.maintenance_cycle_month", ">", 0),
            ]
        )
        stage = self.env["maintenance.stage"].search([], order="sequence", limit=1)
        for asset in assets:
            if not asset.next_maintenance_date or asset.next_maintenance_date > today:
                continue
            open_req = self.search_count(
                [
                    ("equipment_id", "=", asset.id),
                    ("maintenance_type", "=", "preventive"),
                    ("stage_id.done", "=", False),
                ]
            )
            if open_req:
                continue
            self.create(
                {
                    "name": _("Bảo trì định kỳ — %s") % (asset.asset_code or asset.name),
                    "equipment_id": asset.id,
                    "maintenance_type": "preventive",
                    "request_date": today,
                    "stage_id": stage.id,
                    "eam_work_type": _("Vệ sinh / kiểm tra định kỳ"),
                }
            )
            cycle = asset.category_id.maintenance_cycle_month or 0
            if cycle:
                asset.next_maintenance_date = today + relativedelta(months=cycle)

    @api.model
    def _cron_eam_sla_check(self):
        requests = self.search([("stage_id.done", "=", False), ("sla_deadline", "!=", False)])
        requests._compute_sla_state()
        for req in requests.filtered(lambda r: r.sla_state == "breach"):
            req.activity_schedule(
                "mail.mail_activity_data_todo",
                summary=_("Phiếu bảo trì quá hạn SLA"),
                user_id=req.maintenance_team_id.user_id.id or req.user_id.id,
            )
