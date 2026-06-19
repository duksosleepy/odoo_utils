# -*- coding: utf-8 -*-

from odoo.addons.mail.tools.discuss import Store
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestWorkforceVisibilityDiscuss(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        company = cls.env.company

        cls.vp_user = new_test_user(
            cls.env,
            login="workforce_vp_officer",
            groups="hr.group_hr_user",
        )
        cls.vp_officer = cls.env["hr.employee"].create(
            {
                "name": "VP Officer",
                "user_id": cls.vp_user.id,
                "company_id": company.id,
                "mien": "VP",
                "workforce_group": "VP",
                "employee_visibility": "office",
            }
        )
        cls.vp_colleague = cls.env["hr.employee"].create(
            {
                "name": "VP Colleague",
                "company_id": company.id,
                "mien": "VP",
                "workforce_group": "VP",
                "employee_visibility": "office",
            }
        )

        cls.ch_user = new_test_user(
            cls.env,
            login="workforce_ch_officer",
            groups="hr.group_hr_user",
        )
        cls.ch_officer = cls.env["hr.employee"].create(
            {
                "name": "CH Officer",
                "user_id": cls.ch_user.id,
                "company_id": company.id,
                "mien": "Bắc",
                "workforce_group": "CH",
                "employee_visibility": "store",
            }
        )
        cls.ch_colleague = cls.env["hr.employee"].create(
            {
                "name": "CH Colleague",
                "company_id": company.id,
                "mien": "Nam",
                "workforce_group": "CH",
                "employee_visibility": "store",
            }
        )

        cls.admin_user = new_test_user(
            cls.env,
            login="workforce_hr_admin",
            groups="hr.group_hr_manager",
        )

    def test_discuss_layer_not_filtered_by_hr_visibility(self):
        mixin = self.env["hr.employee.access.mixin"]
        self.assertFalse(mixin._hr_employee_discuss_access_applies(self.vp_user))
        self.assertFalse(mixin._hr_employee_discuss_access_applies(self.ch_user))

    def test_vp_officer_sees_only_office_profiles(self):
        employees = self.env["hr.employee"].with_user(self.vp_user).search([])
        visible_ids = set(employees.ids)
        self.assertIn(self.vp_officer.id, visible_ids)
        self.assertIn(self.vp_colleague.id, visible_ids)
        self.assertNotIn(self.ch_colleague.id, visible_ids)

    def test_ch_officer_sees_only_store_profiles(self):
        employees = self.env["hr.employee"].with_user(self.ch_user).search([])
        visible_ids = set(employees.ids)
        self.assertIn(self.ch_officer.id, visible_ids)
        self.assertIn(self.ch_colleague.id, visible_ids)
        self.assertNotIn(self.vp_colleague.id, visible_ids)

    def test_admin_sees_all_profiles(self):
        employees = self.env["hr.employee"].with_user(self.admin_user).search([])
        visible_ids = set(employees.ids)
        self.assertIn(self.vp_colleague.id, visible_ids)
        self.assertIn(self.ch_colleague.id, visible_ids)

    def test_discuss_can_find_cross_group_partner(self):
        partner_model = self.env["res.partner"].with_user(self.vp_user)
        domain = [
            ("user_ids", "!=", False),
            ("user_ids.share", "=", False),
            ("id", "=", self.ch_user.partner_id.id),
        ]
        self.assertTrue(partner_model.search_count(domain))

        partner_model = self.env["res.partner"].with_user(self.ch_user)
        domain = [
            ("user_ids", "!=", False),
            ("user_ids.share", "=", False),
            ("id", "=", self.vp_user.partner_id.id),
        ]
        self.assertTrue(partner_model.search_count(domain))

    def test_discuss_channel_invite_cross_group(self):
        """Discuss invite picker must not apply HR employee visibility."""
        Partner = self.env["res.partner"]
        vp_invite = Partner.with_user(self.vp_user)._search_for_channel_invite(
            Store(), self.ch_user.name, limit=30
        )
        ch_invite = Partner.with_user(self.ch_user)._search_for_channel_invite(
            Store(), self.vp_user.name, limit=30
        )
        self.assertIn(self.ch_user.partner_id.id, vp_invite["partner_ids"])
        self.assertIn(self.vp_user.partner_id.id, ch_invite["partner_ids"])
