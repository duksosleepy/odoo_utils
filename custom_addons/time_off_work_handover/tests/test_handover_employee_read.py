from unittest.mock import patch

from odoo.addons.hr.models.hr_employee import _ALLOW_READ_HR_EMPLOYEE
from odoo.fields import Domain
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestHandoverEmployeeRead(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = new_test_user(
            cls.env,
            login="handover-employee-read",
            groups="base.group_user",
        )
        cls.recipient = cls.env["hr.employee"].create(
            {
                "name": "Restricted Handover Recipient",
                "company_id": cls.user.company_id.id,
            }
        )

    def test_handover_onchange_uses_internal_employee_read_context(self):
        Leave = self.env["hr.leave"].with_user(self.user)

        self.assertTrue(
            Leave._is_handover_onchange(["handover_acceptance_ids"])
        )
        self.assertTrue(
            Leave._is_handover_onchange(
                ["handover_acceptance_ids.employee_id"]
            )
        )
        self.assertFalse(Leave._is_handover_onchange(["request_date_from"]))

        handover_leave = Leave._with_handover_employee_read_context()
        self.assertIs(
            handover_leave.env.context.get("_allow_read_hr_employee"),
            _ALLOW_READ_HR_EMPLOYEE,
        )

        access_mixin_type = type(self.env["hr.employee.access.mixin"])
        with patch.object(
            access_mixin_type,
            "_hr_employee_access_extra_domain",
            autospec=True,
            return_value=Domain.FALSE,
        ):
            Employee = self.env["hr.employee"].with_user(self.user)
            self.assertFalse(
                Employee.search([("id", "=", self.recipient.id)])
            )

            internal_recipient = handover_leave.env["hr.employee"].browse(
                self.recipient.id
            )
            internal_recipient.invalidate_recordset(["name"])
            self.assertEqual(
                internal_recipient.name,
                self.recipient.name,
            )
