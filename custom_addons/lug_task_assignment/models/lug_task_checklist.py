# -*- coding: utf-8 -*-

from odoo import fields, models


class LugTaskChecklist(models.Model):
    _name = "lug.task.checklist"
    _description = "Checklist công việc"
    _order = "sequence, id"

    task_id = fields.Many2one("lug.task", required=True, ondelete="cascade", index=True)
    name = fields.Char(string="Hạng mục", required=True)
    completed = fields.Boolean(string="Hoàn thành", default=False)
    sequence = fields.Integer(default=10)
