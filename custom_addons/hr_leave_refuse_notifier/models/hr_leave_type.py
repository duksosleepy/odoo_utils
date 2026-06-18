# -*- coding: utf-8 -*-
from odoo import fields, models


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    refuse_notify_employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Refuse Ticket Notifier",
        help="Employee who will be notified when a time off request of this type is refused.",
        domain="[('user_id', '!=', False), ('user_id.share', '=', False)]",
    )
