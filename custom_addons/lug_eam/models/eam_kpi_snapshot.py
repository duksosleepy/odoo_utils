# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EamKpiSnapshot(models.Model):
    _name = "eam.kpi.snapshot"
    _description = "Ảnh chụp KPI tài sản"
    _order = "snapshot_date desc"

    snapshot_date = fields.Date(required=True, index=True)
    company_id = fields.Many2one("res.company", required=True, index=True)
    total_asset = fields.Integer(string="Tổng tài sản")
    in_stock = fields.Integer(string="Trong kho")
    in_use = fields.Integer(string="Đang sử dụng")
    maintenance = fields.Integer(string="Đang bảo trì")
    broken = fields.Integer(string="Hỏng")
    disposed = fields.Integer(string="Thanh lý")
    purchase_value = fields.Monetary(string="Giá trị mua (hoạt động)")
    maintenance_cost_mtd = fields.Monetary(string="Chi phí BT tháng")
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )

    _date_company_unique = models.Constraint(
        "unique(snapshot_date, company_id)",
        "Mỗi ngày chỉ một snapshot cho mỗi công ty.",
    )

    @api.model
    def _cron_eam_kpi_snapshot(self):
        today = fields.Date.context_today(self)
        month_start = today.replace(day=1)
        Equipment = self.env["maintenance.equipment"]
        Request = self.env["maintenance.request"]
        for company in self.env.companies:
            assets = Equipment.with_company(company).search(
                [("company_id", "=", company.id), ("active", "=", True)]
            )
            active_assets = assets.filtered(lambda a: a.state != "disposed")
            requests = Request.with_company(company).search(
                [
                    ("company_id", "=", company.id),
                    ("close_date", ">=", month_start),
                    ("close_date", "<=", today),
                    ("stage_id.done", "=", True),
                ]
            )
            vals = {
                "snapshot_date": today,
                "company_id": company.id,
                "total_asset": len(assets),
                "in_stock": len(assets.filtered(lambda a: a.state == "in_stock")),
                "in_use": len(assets.filtered(lambda a: a.state == "in_use")),
                "maintenance": len(assets.filtered(lambda a: a.state == "maintenance")),
                "broken": len(assets.filtered(lambda a: a.state == "broken")),
                "disposed": len(assets.filtered(lambda a: a.state == "disposed")),
                "purchase_value": sum(active_assets.mapped("cost")),
                "maintenance_cost_mtd": sum(requests.mapped("eam_total_cost")),
                "currency_id": company.currency_id.id,
            }
            existing = self.search(
                [("snapshot_date", "=", today), ("company_id", "=", company.id)],
                limit=1,
            )
            if existing:
                existing.write(vals)
            else:
                self.create(vals)
