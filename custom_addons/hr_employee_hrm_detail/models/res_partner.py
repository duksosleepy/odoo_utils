# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.fields import Domain
from odoo.tools import SQL

from odoo.addons.mail.models.res_partner import ResPartner as MailResPartner
from odoo.addons.mail.tools.discuss import Store


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends("employee_ids")
    def _compute_employee(self):
        """Limit partner.employee flag to employees visible under HR scope."""
        mixin = self.env["hr.employee.access.mixin"]
        domain = [("work_contact_id", "in", self.ids)]
        if mixin._hr_employee_discuss_access_applies():
            domain = list(
                mixin._hr_employee_apply_access_domain(domain, model_name="hr.employee")
            )
        employee_data = self.env["hr.employee"]._read_group(
            domain=domain,
            groupby=["work_contact_id"],
        )
        employees = {employee for [employee] in employee_data}
        for partner in self:
            partner.employee = partner in employees

    def _get_store_avatar_card_fields(self, target):
        # Skip hr.res.partner: it prefetches every employee_ids record (Discuss/OdooBot).
        avatar_card_fields = MailResPartner._get_store_avatar_card_fields(self, target)
        if not target.is_internal(self.env):
            return avatar_card_fields
        mixin = self.env["hr.employee.access.mixin"]
        if not mixin._hr_employee_discuss_access_applies():
            employee_fields = self.sudo().employee_ids._get_store_avatar_card_fields(target)
            if self.sudo().employee_ids:
                avatar_card_fields.append(
                    Store.Many("employee_ids", employee_fields, mode="ADD", sudo=True)
                )
            return avatar_card_fields
        domain = [("work_contact_id", "in", self.ids)]
        domain = list(mixin._hr_employee_apply_access_domain(domain, model_name="hr.employee"))
        public_employees = self.env["hr.employee.public"].sudo().search(domain)
        if public_employees:
            employee_fields = self.env["hr.employee"].sudo().browse(
                public_employees.ids
            )._get_store_avatar_card_fields(target)
            avatar_card_fields.append(
                Store.Many(public_employees, employee_fields, mode="ADD", sudo=True)
            )
        return avatar_card_fields

    @api.model
    def _hr_discuss_partner_access_domain(self):
        return self.env["hr.employee.access.mixin"]._hr_employee_discuss_accessible_partner_domain()

    @api.model
    def _search_mention_suggestions(self, domain, limit, extra_domain=None):
        hr_domain = self._hr_discuss_partner_access_domain()
        if hr_domain is not None:
            extra_domain = Domain(extra_domain or Domain.TRUE) & hr_domain
        return super()._search_mention_suggestions(domain, limit, extra_domain)

    @api.readonly
    @api.model
    def _search_for_channel_invite(self, store: Store, search_term, channel_id=None, limit=30):
        domain = Domain.AND(
            [
                Domain("name", "ilike", search_term) | Domain("email", "ilike", search_term),
                [("id", "!=", self.env.user.partner_id.id)],
                [("active", "=", True)],
                [("user_ids", "!=", False)],
                [("user_ids.active", "=", True)],
                [("user_ids.share", "=", False)],
            ]
        )
        hr_domain = self._hr_discuss_partner_access_domain()
        if hr_domain is not None:
            domain &= hr_domain
        channel = self.env["discuss.channel"]
        if channel_id:
            channel = self.env["discuss.channel"].search([("id", "=", int(channel_id))])
            domain &= Domain("channel_ids", "not in", channel.id)
            if channel.group_public_id:
                domain &= Domain("user_ids.all_group_ids", "in", channel.group_public_id.id)
        query = self._search(domain, limit=limit)
        query.order = SQL(
            'LOWER(%s), "res_partner"."id"', self._field_to_sql(self._table, "name")
        )
        selectable_partners = self.env["res.partner"].browse(query)
        selectable_partners._search_for_channel_invite_to_store(store, channel)
        return {
            "count": self.search_count(domain),
            "partner_ids": selectable_partners.ids,
        }
