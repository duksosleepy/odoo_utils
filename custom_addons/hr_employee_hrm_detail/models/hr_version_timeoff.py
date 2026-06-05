from odoo import models


class HrVersionTimeoff(models.Model):
    _inherit = "hr.version"

    def _check_access(self, operation):
        """Allow time-off users to read contract versions they need."""
        if operation == "read" and not self.env.su:
            user = self.env.user
            if user.has_group("hr.group_hr_user") and not user.has_group(
                "hr.group_hr_manager"
            ):
                if not self:
                    return None
                employee_ids = self.mapped("employee_id").ids
                if employee_ids:
                    visible_count = self.env["hr.employee"].search_count(
                        [("id", "in", employee_ids)]
                    )
                    if visible_count == len(set(employee_ids)):
                        return None
            elif not user.has_group("hr.group_hr_user"):
                own = user.employee_id
                if own:
                    if not self:
                        return None
                    if not self.filtered(
                        lambda version: version.employee_id.id != own.id
                    ):
                        return None
        return super()._check_access(operation)
