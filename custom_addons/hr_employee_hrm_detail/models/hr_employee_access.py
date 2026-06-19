# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.fields import Domain

from .hr_employee import (
    VISIBILITY_ALL,
    VISIBILITY_OFFICE,
    VISIBILITY_STORE,
    WORKFORCE_GROUP_CH,
    WORKFORCE_GROUP_VP,
    _workforce_group_from_mien,
)


class HrEmployeeAccessMixin(models.AbstractModel):
    _name = "hr.employee.access.mixin"
    _description = "Workforce visibility / Employees privilege access helpers"

    @api.model
    def _hr_employee_access_self_domain(self, user=None):
        user = user or self.env.user
        return Domain([
            "|",
            ("user_id", "=", user.id),
            ("id", "=", user.employee_id.id),
        ])

    @api.model
    def _hr_employee_time_off_team_domain(self, user=None, model_name=None):
        """Narrow read for time-off approval (leave_manager_id only)."""
        user = user or self.env.user
        # hr.employee.public has leave_manager_id (hr_holidays); never use
        # employee_id.* here or domain SQL sub-searches loop via hr.employee.
        return Domain([("leave_manager_id", "=", user.id)])

    @api.model
    def _hr_employee_access_scope_domain(self, user=None, model_name=None):
        """Own profile plus employees the user may approve time off for."""
        return self._hr_employee_access_self_domain(user) | self._hr_employee_time_off_team_domain(
            user, model_name=model_name
        )

    @api.model
    def _hr_employee_user_mien(self, user=None):
        user = user or self.env.user
        emp = user.employee_id
        if not emp:
            return False
        return emp.mien or (emp.ma_bo_phan_id.mien if emp.ma_bo_phan_id else False)

    @api.model
    def _hr_employee_user_workforce_group(self, user=None):
        user = user or self.env.user
        emp = user.employee_id
        if not emp:
            return False
        if emp.workforce_group:
            return emp.workforce_group
        return _workforce_group_from_mien(self._hr_employee_user_mien(user))

    @api.model
    def _hr_employee_allowed_visibility(self, user=None):
        """Employee visibility layer: office/store scopes for HR profile reads."""
        user = user or self.env.user
        workforce_group = self._hr_employee_user_workforce_group(user)
        if workforce_group == WORKFORCE_GROUP_VP:
            return [VISIBILITY_OFFICE]
        if workforce_group == WORKFORCE_GROUP_CH:
            return [VISIBILITY_STORE]
        return []

    @api.model
    def _hr_employee_visibility_match_domain(
        self, visibility_field, allowed_visibility, user=None, model_name=None
    ):
        user = user or self.env.user
        return Domain([
            (visibility_field, "in", list(allowed_visibility)),
        ]) | self._hr_employee_access_scope_domain(user, model_name=model_name)

    @api.model
    def _hr_employee_apply_access_domain(self, domain, model_name=None):
        model_name = model_name or "hr.employee"
        extra = self._hr_employee_access_extra_domain(model_name=model_name)
        if extra is not None:
            return Domain(domain) & extra
        return Domain(domain)

    @api.model
    def _hr_employee_access_field_names(self, model_name):
        if model_name == "hr.employee.public":
            return "employee_id.employee_visibility", "employee_id.workforce_group"
        return "employee_visibility", "workforce_group"

    @api.model
    def _hr_employee_staff_store_employee_ids(self, user=None):
        """Same-store employee ids (SQL) for staff; avoids hr.employee _search loops."""
        user = user or self.env.user
        emp = user.sudo().employee_id
        if not emp or not emp.ma_bo_phan_id:
            return []
        self.env.cr.execute(
            "SELECT id FROM hr_employee WHERE ma_bo_phan_id = %s",
            (emp.ma_bo_phan_id.id,),
        )
        return [row[0] for row in self.env.cr.fetchall()]

    @api.model
    def _hr_employee_staff_department_domain(self, user=None, model_name=None):
        """Employees privilege = Employee: same ma_bo_phan_id (+ own profile)."""
        user = user or self.env.user
        store_ids = self._hr_employee_staff_store_employee_ids(user)
        if not store_ids:
            return self._hr_employee_access_scope_domain(user, model_name=model_name)
        return Domain([("id", "in", store_ids)]) | self._hr_employee_access_scope_domain(
            user, model_name=model_name
        )

    @api.model
    def _hr_employee_access_extra_domain(self, user=None, model_name=None):
        """Extra AND domain; None = no additional restriction."""
        user = user or self.env.user
        model_name = model_name or "hr.employee"
        if user._is_superuser() or user.has_group("hr.group_hr_manager"):
            return None
        if user.has_group("hr_employee_hrm_detail.group_hr_employees_supporter"):
            return None
        if user.has_group("hr_employee_hrm_detail.group_hr_employees_staff"):
            return self._hr_employee_staff_department_domain(user, model_name=model_name)
        if not user.has_group("hr.group_hr_user"):
            return None
        allowed_visibility = self._hr_employee_allowed_visibility(user)
        if not allowed_visibility:
            return self._hr_employee_access_scope_domain(user, model_name=model_name)
        visibility_field, _workforce_field = self._hr_employee_access_field_names(model_name)
        return self._hr_employee_visibility_match_domain(
            visibility_field,
            allowed_visibility,
            user=user,
            model_name=model_name,
        )

    @api.model
    def _hr_employee_discuss_access_applies(self, user=None):
        """Communication layer: Discuss must not follow HR employee visibility."""
        return False
