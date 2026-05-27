from odoo import api, models


class HrLeave(models.Model):
    _inherit = "hr.leave"

    def _employees_no_timeoff_context(self):
        employee = self.env.user.employee_id
        return {
            "employees_no_timeoff_write": True,
            "employees_no_allowed_employee_ids": [employee.id] if employee else [],
        }

    @api.model_create_multi
    def create(self, vals_list):
        return super(HrLeave, self.with_context(**self._employees_no_timeoff_context())).create(vals_list)

    def write(self, vals):
        return super(HrLeave, self.with_context(**self._employees_no_timeoff_context())).write(vals)

    def action_confirm(self):
        return super(HrLeave, self.with_context(**self._employees_no_timeoff_context())).action_confirm()
