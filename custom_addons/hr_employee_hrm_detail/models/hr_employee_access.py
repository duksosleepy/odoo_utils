# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.fields import Domain

MIEN_BND = ("Bắc", "Nam", "ĐTT")


class HrEmployeeAccessMixin(models.AbstractModel):
    _name = "hr.employee.access.mixin"
    _description = "Miền / Employees privilege access helpers"

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
    def _hr_employee_allowed_miens(self, user=None):
        user = user or self.env.user
        mien = self._hr_employee_user_mien(user)
        if mien == "VP":
            return ["VP"]
        if mien in MIEN_BND:
            return list(MIEN_BND)
        return []

    @api.model
    def _hr_employee_mien_match_domain(
        self, mien_field, dept_mien_field, allowed, user=None, model_name=None
    ):
        user = user or self.env.user
        return Domain([
            "|",
            (mien_field, "in", allowed),
            "&",
            (mien_field, "=", False),
            (dept_mien_field, "in", allowed),
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
            return "employee_id.mien", "employee_id.ma_bo_phan_id.mien"
        return "mien", "ma_bo_phan_id.mien"

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
        allowed = self._hr_employee_allowed_miens(user)
        if not allowed:
            return self._hr_employee_access_scope_domain(user, model_name=model_name)
        mien_field, dept_mien_field = self._hr_employee_access_field_names(model_name)
        return self._hr_employee_mien_match_domain(
            mien_field, dept_mien_field, allowed, user=user, model_name=model_name
        )

    @api.model
    def _hr_employee_discuss_access_applies(self, user=None):
        """Whether Discuss partner pickers must follow HR employee visibility."""
        user = user or self.env.user
        if user._is_superuser() or user.has_group("hr.group_hr_manager"):
            return False
        return user.has_group(
            "hr_employee_hrm_detail.group_hr_employees_staff"
        ) or user.has_group("hr.group_hr_user")

    @api.model
    def _hr_employee_discuss_accessible_partner_domain(self, user=None):
        """res.partner domain for Discuss search/invite; None = no HR filter."""
        user = user or self.env.user
        if not self._hr_employee_discuss_access_applies(user):
            return None
        employee_domain = self._hr_employee_apply_access_domain(
            [], model_name="hr.employee.public"
        )
        employees = self.env["hr.employee.public"].with_user(user).search(employee_domain)
        partner_ids = employees.user_id.partner_id.ids
        partner_ids = list({user.partner_id.id, *partner_ids})
        return Domain([("id", "in", partner_ids)])
