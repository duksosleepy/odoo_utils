# Part of Odoo. See LICENSE file for full copyright and licensing details.

from functools import partial

from odoo import _, api, models
from odoo.exceptions import AccessError

from .hr_employee_privacy import (
    _privacy_is_employee_edit_forbidden,
    _privacy_raise_if_department_create_forbidden,
    _privacy_raise_if_department_no_write,
)


class HrDepartment(models.Model):
    _inherit = "hr.department"

    def _check_access(self, operation):
        if (
            operation in ("create", "write", "unlink")
            and not self.env.su
            and _privacy_is_employee_edit_forbidden(self.env)
        ):
            messages = {
                "create": _("Bạn không có quyền tạo phòng ban."),
                "write": _("Bạn không có quyền chỉnh sửa phòng ban."),
                "unlink": _("Bạn không có quyền xóa phòng ban."),
            }
            return self, partial(AccessError, messages[operation])
        return super()._check_access(operation)

    @api.model_create_multi
    def create(self, vals_list):
        _privacy_raise_if_department_create_forbidden(self.env)
        return super().create(vals_list)

    def write(self, vals):
        _privacy_raise_if_department_no_write(self.env)
        return super().write(vals)

    def unlink(self):
        _privacy_raise_if_department_no_write(self.env)
        return super().unlink()
