# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LugTaskTimesheet(models.Model):
    _name = "lug.task.timesheet"
    _description = "Timesheet công việc"
    _order = "work_date desc, id desc"

    task_id = fields.Many2one("lug.task", required=True, ondelete="cascade", index=True)
    employee_id = fields.Many2one("hr.employee", string="Nhân viên", required=True)
    work_date = fields.Date(string="Ngày làm", required=True, default=fields.Date.context_today)
    hours = fields.Float(string="Giờ", required=True)
    company_id = fields.Many2one(related="task_id.company_id", store=True)

    @api.constrains("hours")
    def _check_hours(self):
        for line in self:
            if line.hours <= 0:
                raise ValidationError("Số giờ phải lớn hơn 0.")
