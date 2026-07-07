# -*- coding: utf-8 -*-

from odoo import api, fields, models


class LugEmailAccess(models.Model):
    _name = "lug.email.access"
    _description = "Phân quyền xem email"
    _order = "user_id"
    _rec_name = "user_id"

    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        ondelete="cascade",
        index=True,
    )
    group_id = fields.Many2one(
        "res.groups",
        string="Nhóm quyền",
        required=True,
        domain="[('id', 'in', allowed_group_ids)]",
    )
    allowed_group_ids = fields.Many2many(
        "res.groups",
        compute="_compute_allowed_group_ids",
    )
    active = fields.Boolean(string="Hoạt động", default=True)
    line_ids = fields.One2many(
        "lug.email.access.line",
        "access_id",
        string="Phạm vi xem",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Công ty",
        default=lambda self: self.env.company,
    )

    _user_unique = models.Constraint(
        "unique(user_id)",
        "Mỗi user chỉ có một cấu hình phân quyền email.",
    )

    @api.depends_context("uid")
    def _compute_allowed_group_ids(self):
        group_ids = [
            self.env.ref("lug_email_account.group_lug_email_user").id,
            self.env.ref("lug_email_account.group_lug_email_manager").id,
            self.env.ref("lug_email_account.group_lug_email_admin").id,
        ]
        for record in self:
            record.allowed_group_ids = [(6, 0, group_ids)]

    @api.model
    def _lug_email_group_ids(self):
        return [
            self.env.ref("lug_email_account.group_lug_email_user").id,
            self.env.ref("lug_email_account.group_lug_email_manager").id,
            self.env.ref("lug_email_account.group_lug_email_admin").id,
        ]

    @api.model
    def _default_group_id(self):
        return self.env.ref("lug_email_account.group_lug_email_user").id

    @api.model
    def _department_line_values(self):
        departments = self.env["hr.department"].search([], order="name")
        return [
            (0, 0, {"department_id": department.id, "can_view": False})
            for department in departments
        ]

    @api.model_create_multi
    def create(self, vals_list):
        prepared = []
        for vals in vals_list:
            vals = dict(vals)
            if not vals.get("group_id"):
                vals["group_id"] = self._default_group_id()
            if not vals.get("line_ids"):
                vals["line_ids"] = self._department_line_values()
            prepared.append(vals)
        records = super().create(prepared)
        records._sync_user_access()
        return records

    def write(self, vals):
        res = super().write(vals)
        if any(
            key in vals
            for key in ("user_id", "group_id", "active", "line_ids")
        ):
            self._sync_user_access()
        return res

    def unlink(self):
        users = self.user_id
        res = super().unlink()
        users._sync_lug_email_scope_from_access()
        return res

    def action_reload_departments(self):
        Department = self.env["hr.department"]
        for access in self:
            existing = {line.department_id.id: line for line in access.line_ids}
            commands = []
            for department in Department.search([], order="name"):
                line = existing.get(department.id)
                if line:
                    continue
                commands.append(
                    (0, 0, {"department_id": department.id, "can_view": False})
                )
            if commands:
                access.write({"line_ids": commands})
        return True

    def _sync_user_access(self):
        for access in self.filtered("user_id"):
            access.user_id._sync_lug_email_scope_from_access(access)
            access._sync_user_groups()

    def _sync_user_groups(self):
        lug_groups = self.env["res.groups"].browse(self._lug_email_group_ids())
        for access in self.filtered(lambda rec: rec.active and rec.user_id):
            user = access.user_id
            groups = user.group_ids - lug_groups
            if access.group_id:
                groups |= access.group_id
            user.sudo().write({"group_ids": [(6, 0, groups.ids)]})

    @api.onchange("user_id")
    def _onchange_user_id(self):
        if not self.user_id:
            return
        lug_groups = self.env["res.groups"].browse(self._lug_email_group_ids())
        current = self.user_id.group_ids & lug_groups
        if current:
            self.group_id = current[:1]
        elif not self.group_id:
            self.group_id = self._default_group_id()


class LugEmailAccessLine(models.Model):
    _name = "lug.email.access.line"
    _description = "Phạm vi xem email theo phòng ban"
    _order = "department_id"

    access_id = fields.Many2one(
        "lug.email.access",
        required=True,
        ondelete="cascade",
        index=True,
    )
    department_id = fields.Many2one(
        "hr.department",
        string="Phòng ban",
        required=True,
        ondelete="cascade",
    )
    can_view = fields.Boolean(string="Được xem", default=False)

    _department_unique = models.Constraint(
        "unique(access_id, department_id)",
        "Phòng ban đã tồn tại trong phạm vi xem.",
    )

    def write(self, vals):
        res = super().write(vals)
        if "can_view" in vals:
            self.access_id.user_id._sync_lug_email_scope_from_access(self.access_id)
        return res
