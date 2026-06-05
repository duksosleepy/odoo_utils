# -*- coding: utf-8 -*-

from odoo import api, fields, models

from .hr_employee_access import MIEN_BND


class ResUsers(models.Model):
    _inherit = "res.users"

    employee_ma_bo_phan_id = fields.Many2one(
        "hr.store.code",
        string="Mã bộ phận (nhân viên)",
        compute="_compute_employee_ma_bo_phan_id",
        store=True,
        index=True,
    )

    hr_officer_mien_scope = fields.Selection(
        selection=[
            ("vp", "VP"),
            ("bnd", "Bắc/Nam/ĐTT"),
            ("self", "Self only"),
        ],
        compute="_compute_hr_officer_mien_scope",
        store=True,
    )

    @api.depends("employee_id", "employee_id.ma_bo_phan_id")
    def _compute_employee_ma_bo_phan_id(self):
        for user in self:
            emp = user.sudo().employee_id
            user.employee_ma_bo_phan_id = emp.ma_bo_phan_id if emp else False

    @api.depends(
        "employee_id.mien",
        "employee_id.ma_bo_phan_id.mien",
        "group_ids",
    )
    def _compute_hr_officer_mien_scope(self):
        for user in self:
            if user._is_superuser() or user.has_group("hr.group_hr_manager"):
                user.hr_officer_mien_scope = False
                continue
            if user.has_group("hr_employee_hrm_detail.group_hr_employees_supporter"):
                user.hr_officer_mien_scope = False
                continue
            if not user.has_group("hr.group_hr_user"):
                user.hr_officer_mien_scope = False
                continue
            emp = user.employee_id
            mien = False
            if emp:
                mien = emp.mien or (emp.ma_bo_phan_id.mien if emp.ma_bo_phan_id else False)
            if mien == "VP":
                user.hr_officer_mien_scope = "vp"
            elif mien in MIEN_BND:
                user.hr_officer_mien_scope = "bnd"
            else:
                user.hr_officer_mien_scope = "self"

    def write(self, vals):
        res = super().write(vals)
        if "group_ids" in vals:
            self.env.registry.clear_cache()
        return res

    @api.depends("employee_ids")
    def _compute_company_employee(self):
        """Limit company employee to HR visibility scope (Discuss, mentions, etc.)."""
        mixin = self.env["hr.employee.access.mixin"]
        company_domain = [
            ("user_id", "in", self.ids),
            ("company_id", "=", self.env.company.id),
        ]
        if mixin._hr_employee_discuss_access_applies():
            domain = mixin._hr_employee_apply_access_domain(
                company_domain, model_name="hr.employee.public"
            )
            public_emps = self.env["hr.employee.public"].search(domain)
            employees = self.env["hr.employee"].browse(public_emps.ids)
        else:
            employees = self.env["hr.employee"].search(company_domain)
        employee_per_user = {employee.user_id: employee for employee in employees}
        for user in self:
            user.employee_id = employee_per_user.get(user)
