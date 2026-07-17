# -*- coding: utf-8 -*-

"""Tích hợp tùy chọn với lug_permission — chỉ đọc, không sửa module LUG Permission."""

from odoo import api, models


class LugTaskLugAccess(models.Model):
    _inherit = "lug.task"

    @api.model
    def _lug_permission_installed(self):
        return bool(
            self.env["ir.module.module"]
            .sudo()
            .search([("name", "=", "lug_permission"), ("state", "=", "installed")], limit=1)
        )

    @api.model
    def _lug_task_permission_scope_domain(self):
        user = self.env.user
        if not self._lug_permission_installed():
            return []
        if not user.sudo()._lug_permission_is_enforced():
            return []
        if user.has_group("lug_task_assignment.group_lug_task_admin"):
            return []
        scope = user.lug_data_scope or "self"
        if scope == "company":
            return []
        if scope == "department" and user.employee_id.department_id:
            return [("department_id", "child_of", user.employee_id.department_id.id)]
        if scope == "team" and user.employee_id.department_id:
            return [("department_id", "=", user.employee_id.department_id.id)]
        employee = user.sudo().employee_id
        if employee:
            return [
                "|",
                ("assigned_to_id", "=", employee.id),
                ("assigned_by_id", "=", employee.id),
            ]
        return [("id", "=", 0)]

    @api.model
    def search(self, domain, offset=0, limit=None, order=None):
        extra = self._lug_task_permission_scope_domain()
        if extra:
            domain = list(domain or []) + extra
        return super().search(domain, offset=offset, limit=limit, order=order)
