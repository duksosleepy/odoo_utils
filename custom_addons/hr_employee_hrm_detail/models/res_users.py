# -*- coding: utf-8 -*-

from odoo import api, fields, models

from .hr_employee import (
    STORE_MIENS,
    VISIBILITY_OFFICE,
    VISIBILITY_STORE,
    WORKFORCE_GROUP_CH,
    WORKFORCE_GROUP_VP,
    _workforce_group_from_mien,
)


class ResUsers(models.Model):
    _inherit = "res.users"

    employee_ma_bo_phan_id = fields.Many2one(
        "hr.store.code",
        string="Mã bộ phận (nhân viên)",
        compute="_compute_employee_ma_bo_phan_id",
        store=True,
        index=True,
    )

    hr_user_workforce_scope = fields.Selection(
        selection=[
            ("vp", "Văn phòng"),
            ("ch", "Cửa hàng"),
            ("self", "Self only"),
        ],
        compute="_compute_hr_user_workforce_scope",
        store=True,
    )

    @api.depends("employee_id", "employee_id.ma_bo_phan_id")
    def _compute_employee_ma_bo_phan_id(self):
        for user in self:
            emp = user.sudo().employee_id
            user.employee_ma_bo_phan_id = emp.ma_bo_phan_id if emp else False

    @api.depends(
        "employee_id.workforce_group",
        "employee_id.mien",
        "employee_id.ma_bo_phan_id.mien",
        "group_ids",
    )
    def _compute_hr_user_workforce_scope(self):
        for user in self:
            if user._is_superuser() or user.has_group("hr.group_hr_manager"):
                user.hr_user_workforce_scope = False
                continue
            if user.has_group("hr_employee_hrm_detail.group_hr_employees_supporter"):
                user.hr_user_workforce_scope = False
                continue
            if not user.has_group("hr.group_hr_user"):
                user.hr_user_workforce_scope = False
                continue
            emp = user.employee_id
            workforce_group = False
            if emp:
                workforce_group = emp.workforce_group or _workforce_group_from_mien(
                    emp.mien or (emp.ma_bo_phan_id.mien if emp.ma_bo_phan_id else False)
                )
            if workforce_group == WORKFORCE_GROUP_VP:
                user.hr_user_workforce_scope = "vp"
            elif workforce_group == WORKFORCE_GROUP_CH:
                user.hr_user_workforce_scope = "ch"
            else:
                user.hr_user_workforce_scope = "self"

    def write(self, vals):
        res = super().write(vals)
        if "group_ids" in vals:
            self.env.registry.clear_cache()
        return res
