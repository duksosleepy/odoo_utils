# -*- coding: utf-8 -*-

from odoo import fields, models


class LugTaskHistory(models.Model):
    _name = "lug.task.history"
    _description = "Lịch sử thay đổi công việc"
    _order = "create_date desc, id desc"

    task_id = fields.Many2one("lug.task", required=True, ondelete="cascade", index=True)
    action = fields.Char(string="Hành động", required=True)
    old_value = fields.Text(string="Giá trị cũ")
    new_value = fields.Text(string="Giá trị mới")
    created_by_id = fields.Many2one("res.users", string="Người thực hiện")
