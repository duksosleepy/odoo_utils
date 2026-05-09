from odoo import api, fields, models


class HrLeaveTypeSpecialEmployeeLine(models.Model):
    _name = "hr.leave.type.special.employee.line"
    _description = "Time Off Type — special employees requiring all directors approval"
    _order = "sequence, id"

    leave_type_id = fields.Many2one(
        comodel_name="hr.leave.type",
        string="Time Off Type",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(
        string="STT",
        default=1,
        required=True,
    )
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        required=True,
        ondelete="cascade",
    )

    _sql_constraints = [
        (
            "leave_type_employee_unique",
            "unique(leave_type_id, employee_id)",
            "Each employee can only appear once in the special list for this time off type.",
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            ltid = vals.get("leave_type_id")
            if ltid and ("sequence" not in vals or vals.get("sequence") in (None, False)):
                max_seq = max(
                    self.search([("leave_type_id", "=", ltid)]).mapped("sequence") or [0]
                )
                vals["sequence"] = max_seq + 1
        return super().create(vals_list)
