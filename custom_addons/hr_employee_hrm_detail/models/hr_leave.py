from odoo import models


class HrLeaveTimeOffSummary(models.Model):
    _inherit = 'hr.leave'

    def _recompute_employee_time_off_summary(self):
        employees = self.mapped('employee_id').filtered(lambda e: e.id)
        if employees:
            employees._compute_time_off_summary()

    def action_confirm(self):
        res = super().action_confirm()
        self._recompute_employee_time_off_summary()
        return res

    def action_validate(self):
        res = super().action_validate()
        self._recompute_employee_time_off_summary()
        return res

    def action_refuse(self):
        res = super().action_refuse()
        self._recompute_employee_time_off_summary()
        return res

    def action_draft(self):
        res = super().action_draft()
        self._recompute_employee_time_off_summary()
        return res
