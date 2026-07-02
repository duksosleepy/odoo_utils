# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .lug_constants import LUG_PERMISSION_FIELDS


class LugUserPermission(models.Model):
    _name = "lug.user.permission"
    _description = "LUG User Extra Permission"
    _inherit = "lug.permission.line.mixin"
    _order = "app_id"

    user_id = fields.Many2one(
        "res.users",
        required=True,
        ondelete="cascade",
        index=True,
    )

    _user_app_unique = models.Constraint(
        "unique(user_id, app_id)",
        "Each application can only appear once in extra user permissions.",
    )

    @api.constrains(
        "perm_view",
        "perm_create",
        "perm_edit",
        "perm_delete",
        "perm_approve",
        "perm_export",
        "perm_import",
        "perm_print",
        "perm_admin",
    )
    def _check_view_required_for_actions(self):
        for line in self:
            if line.perm_view:
                continue
            if any(
                line[field_name]
                for field_name, _code in LUG_PERMISSION_FIELDS
                if field_name != "perm_view"
            ):
                raise ValidationError(
                    self.env._(
                        "Application '%(app)s': enable View before granting other actions.",
                        app=line.app_id.display_name,
                    )
                )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines.user_id._sync_lug_odoo_groups()
        lines.user_id._sync_lug_visibility_policy()
        self.env["res.users"]._lug_clear_menu_cache_global(self.env)
        return lines

    def write(self, vals):
        res = super().write(vals)
        if any(
            key.startswith("perm_") or key in {"app_id", "user_id"}
            for key in vals
        ):
            self.user_id._sync_lug_odoo_groups()
            self.user_id._sync_lug_visibility_policy()
            self.env["res.users"]._lug_clear_menu_cache_global(self.env)
        return res

    def unlink(self):
        users = self.user_id
        res = super().unlink()
        users._sync_lug_odoo_groups()
        users._sync_lug_visibility_policy()
        self.env["res.users"]._lug_clear_menu_cache_global(self.env)
        return res
