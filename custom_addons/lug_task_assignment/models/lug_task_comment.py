# -*- coding: utf-8 -*-

from odoo import fields, models


class LugTaskComment(models.Model):
    _name = "lug.task.comment"
    _description = "Bình luận công việc"
    _order = "create_date desc"

    task_id = fields.Many2one("lug.task", required=True, ondelete="cascade", index=True)
    employee_id = fields.Many2one("hr.employee", string="Nhân viên")
    comment = fields.Html(string="Nội dung", required=True)
    company_id = fields.Many2one(
        related="task_id.company_id",
        store=True,
        index=True,
    )
