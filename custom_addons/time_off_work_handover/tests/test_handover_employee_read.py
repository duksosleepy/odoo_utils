from datetime import date, datetime, time
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
        cls.requester_employee = cls.env["hr.employee"].create(
            {
                "name": "Handover Requester",
                "user_id": cls.user.id,
                "company_id": cls.user.company_id.id,
            }
        )
        cls.leave_type = cls.env["hr.leave.type"].create(
            {
                "name": "Handover overlap test",
                "requires_allocation": False,
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

        self.assertTrue(
            Leave._needs_handover_read_context(["request_date_from"], {})
        )
        self.assertTrue(
            Leave._needs_handover_read_context(
                [],
                {"unavailable_handover_employee_ids": {"fields": {}}},
            )
        )
        self.assertFalse(
            Leave._needs_handover_read_context(["name"], {"name": {}})
        )

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

    def test_handover_onchange_marks_nested_employee_serialization(self):
        Leave = self.env["hr.leave"]
        original = {
            "handover_employee_ids": {"fields": {"display_name": {}}},
            "unavailable_handover_employee_ids": {"fields": {"display_name": {}}},
            "handover_acceptance_ids": {
                "fields": {
                    "employee_id": {"fields": {"display_name": {}}},
                    "handover_work_content": {},
                }
            },
            "name": {},
        }

        prepared = Leave._handover_onchange_fields_spec(original)

        self.assertIs(
            prepared["unavailable_handover_employee_ids"]["context"][
                "_allow_read_hr_employee"
            ],
            _ALLOW_READ_HR_EMPLOYEE,
        )
        self.assertIs(
            prepared["handover_employee_ids"]["context"][
                "_allow_read_hr_employee"
            ],
            _ALLOW_READ_HR_EMPLOYEE,
        )
        self.assertIs(
            prepared["handover_acceptance_ids"]["context"][
                "_allow_read_hr_employee"
            ],
            _ALLOW_READ_HR_EMPLOYEE,
        )
        self.assertIs(
            prepared["handover_acceptance_ids"]["fields"]["employee_id"][
                "context"
            ]["_allow_read_hr_employee"],
            _ALLOW_READ_HR_EMPLOYEE,
        )
        self.assertNotIn("context", original["handover_employee_ids"])
        self.assertNotIn(
            "context",
            original["handover_acceptance_ids"]["fields"]["employee_id"],
        )

    def test_unavailable_handover_employees_on_overlapping_dates(self):
        overlap_day = date(2026, 6, 26)
        start_dt = datetime.combine(overlap_day, time(7, 0))
        end_dt = datetime.combine(overlap_day, time(19, 0))

        self.env["hr.leave"].sudo().create(
            {
                "name": "Colleague leave",
                "employee_id": self.recipient.id,
                "holiday_status_id": self.leave_type.id,
                "request_date_from": overlap_day,
                "request_date_to": overlap_day,
                "date_from": start_dt,
                "date_to": end_dt,
                "state": "confirm",
            }
        )

        Leave = self.env["hr.leave"].with_user(self.user)
        draft = Leave.new(
            {
                "employee_id": self.requester_employee.id,
                "holiday_status_id": self.leave_type.id,
                "request_date_from": overlap_day,
                "request_date_to": overlap_day,
                "date_from": start_dt,
                "date_to": end_dt,
            }
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

            draft._compute_unavailable_handover_employee_ids()
            unavailable = draft.unavailable_handover_employee_ids
            self.assertIn(self.recipient.id, unavailable.ids)
            self.assertEqual(
                unavailable.mapped("name"),
                [self.recipient.name],
            )
