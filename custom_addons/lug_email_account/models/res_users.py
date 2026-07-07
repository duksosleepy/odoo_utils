# -*- coding: utf-8 -*-

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    lug_email_allowed_department_ids = fields.Many2many(
        "hr.department",
        "res_users_lug_email_department_rel",
        "user_id",
        "department_id",
        string="Phòng ban được xem email",
    )
    lug_email_scope_unrestricted = fields.Boolean(
        string="Xem toàn bộ email",
        default=False,
    )

    def _sync_lug_email_scope_from_access(self, access=None):
        Access = self.env["lug.email.access"].sudo()
        admin_group = self.env.ref(
            "lug_email_account.group_lug_email_admin",
            raise_if_not_found=False,
        )
        all_departments = self.env["hr.department"].search([])
        for user in self:
            if admin_group and admin_group in user.all_group_ids:
                user.sudo().write(
                    {
                        "lug_email_scope_unrestricted": True,
                        "lug_email_allowed_department_ids": [(6, 0, all_departments.ids)],
                    }
                )
                continue
            record = access if access and access.user_id == user else Access.search(
                [("user_id", "=", user.id), ("active", "=", True)],
                limit=1,
            )
            if record:
                dept_ids = record.line_ids.filtered("can_view").mapped(
                    "department_id"
                ).ids
                user.sudo().write(
                    {
                        "lug_email_scope_unrestricted": False,
                        "lug_email_allowed_department_ids": [(6, 0, dept_ids)],
                    }
                )
            else:
                user.sudo().write(
                    {
                        "lug_email_scope_unrestricted": False,
                        "lug_email_allowed_department_ids": [(5, 0, 0)],
                    }
                )
        return True

    def _lug_email_scope_domain(self):
        self.ensure_one()
        if self.lug_email_scope_unrestricted:
            return []
        allowed = self.lug_email_allowed_department_ids
        if not allowed:
            return [("id", "=", 0)]
        return [
            "|",
            ("department_id", "in", allowed.ids),
            "&",
            ("department_id", "=", False),
            ("department", "in", allowed.mapped("name")),
        ]
