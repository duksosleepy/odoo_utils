# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError

GROUP_LEAVE_DELETE = "hr_leave_delete_cancel.group_hr_holidays_leave_delete"


class HrLeave(models.Model):
    _inherit = "hr.leave"

    def _has_leave_delete_cancel_permission(self):
        user = self.env.user
        return user._is_superuser() or user.has_group(GROUP_LEAVE_DELETE)

    def _is_own_leave(self):
        self.ensure_one()
        return bool(self.employee_id) and self.employee_id in self.env.user.employee_ids

    def _check_leave_delete_cancel_permission(self):
        """Block delete/cancel on other employees' time off without explicit permission."""
        if self._has_leave_delete_cancel_permission():
            return
        user_employees = self.env.user.employee_ids
        if any(not leave.employee_id or leave.employee_id not in user_employees for leave in self):
            raise UserError(
                _("You are not allowed to delete or cancel time off requests of employees.")
            )

    @api.ondelete(at_uninstall=False)
    def _unlink_if_leave_delete_permission(self):
        self._check_leave_delete_cancel_permission()

    def _action_user_cancel(self, reason=None):
        self._check_leave_delete_cancel_permission()
        return super()._action_user_cancel(reason=reason)

    def _get_next_states_by_state(self):
        self.ensure_one()
        state_result = super()._get_next_states_by_state()
        if self._has_leave_delete_cancel_permission():
            return state_result
        if self.employee_id and self.employee_id in self.env.user.employee_ids:
            return state_result
        for states in state_result.values():
            states.discard("cancel")
        return state_result
