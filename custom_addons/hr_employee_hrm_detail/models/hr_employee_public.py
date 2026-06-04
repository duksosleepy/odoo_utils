# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.fields import Domain


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    def _hr_employee_read_is_restricted(self):
        return (
            self.env["hr.employee.access.mixin"]._hr_employee_access_extra_domain(
                model_name="hr.employee.public"
            )
            is not None
        )

    def _hr_employee_filter_accessible(self):
        if not self._hr_employee_read_is_restricted():
            return self
        if not self.ids:
            return self
        mixin = self.env["hr.employee.access.mixin"]
        domain = mixin._hr_employee_apply_access_domain(
            [("id", "in", self.ids)],
            model_name="hr.employee.public",
        )
        return self.search(domain)

    def _filtered_access(self, operation):
        records = super()._filtered_access(operation)
        if operation == "read" and self._hr_employee_read_is_restricted():
            allowed = self.browse(records.ids)._hr_employee_filter_accessible()
            return records.browse(allowed.ids)
        return records

    def _check_access(self, operation):
        if operation == "read" and self.ids and self._hr_employee_read_is_restricted():
            allowed = self._hr_employee_filter_accessible()
            if allowed:
                return super(HrEmployeePublic, allowed)._check_access(operation)
            return None
        return super()._check_access(operation)

    def read(self, fields=None, load="_classic_read"):
        if not self._hr_employee_read_is_restricted():
            return super().read(fields, load)
        allowed = self._hr_employee_filter_accessible()
        if not allowed:
            return []
        return super(HrEmployeePublic, allowed).read(fields, load)

    def fetch(self, field_names):
        if not self._hr_employee_read_is_restricted():
            return super().fetch(field_names)
        allowed = self._hr_employee_filter_accessible()
        if allowed:
            super(HrEmployeePublic, allowed).fetch(field_names)
        return

    def web_read(self, specification):
        return super(HrEmployeePublic, self._hr_employee_filter_accessible()).web_read(
            specification
        )

    @api.model
    def _search(
        self,
        domain,
        offset=0,
        limit=None,
        order=None,
        *,
        active_test=True,
        bypass_access=False,
    ):
        domain = list(
            self.env["hr.employee.access.mixin"]._hr_employee_apply_access_domain(
                domain, model_name=self._name
            )
        )
        return super()._search(
            domain,
            offset=offset,
            limit=limit,
            order=order,
            active_test=active_test,
            bypass_access=bypass_access,
        )

    @api.model
    def search_fetch(self, domain, field_names=None, offset=0, limit=None, order=None):
        domain = list(
            self.env["hr.employee.access.mixin"]._hr_employee_apply_access_domain(
                domain, model_name=self._name
            )
        )
        return super().search_fetch(domain, field_names, offset, limit, order)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        domain = list(domain or [])
        if self._hr_employee_read_is_restricted():
            extra = self.env["hr.employee.access.mixin"]._hr_employee_apply_access_domain(
                domain, model_name="hr.employee.public"
            )
            domain = list(Domain(domain) & extra)
        return super().search_read(
            domain, fields, offset, limit, order, **read_kwargs
        )

    @api.model
    def web_search_read(self, domain, specification, offset=0, limit=None, order=None, count_limit=None):
        domain = list(domain or [])
        if self._hr_employee_read_is_restricted():
            extra = self.env["hr.employee.access.mixin"]._hr_employee_apply_access_domain(
                domain, model_name="hr.employee.public"
            )
            domain = list(Domain(domain) & extra)
        return super().web_search_read(
            domain, specification, offset=offset, limit=limit, order=order, count_limit=count_limit
        )
