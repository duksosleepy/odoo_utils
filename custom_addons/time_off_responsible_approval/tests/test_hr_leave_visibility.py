from datetime import date

from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestHrLeaveVisibility(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.approver = new_test_user(
            cls.env,
            login="time-off-limited-approver",
            groups="hr_holidays.group_hr_holidays_user",
        )
        cls.limited_approver = new_test_user(
            cls.env,
            login="time-off-actionable-approver",
            groups="base.group_user",
        )
        cls.owner = new_test_user(
            cls.env,
            login="time-off-owner",
            groups="base.group_user",
        )
        cls.other_owner = new_test_user(
            cls.env,
            login="time-off-other-owner",
            groups="base.group_user",
        )
        cls.approver_employee = cls.env["hr.employee"].create(
            {
                "name": "Limited Approver",
                "user_id": cls.approver.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.limited_approver_employee = cls.env["hr.employee"].create(
            {
                "name": "Actionable Approver",
                "user_id": cls.limited_approver.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.owner_employee = cls.env["hr.employee"].create(
            {
                "name": "Ticket Owner",
                "user_id": cls.owner.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.other_employee = cls.env["hr.employee"].create(
            {
                "name": "Unrelated Ticket Owner",
                "user_id": cls.other_owner.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.leave_type = cls.env["hr.leave.type"].create(
            {
                "name": "Visibility security test",
                "requires_allocation": False,
                "company_id": cls.env.company.id,
            }
        )
        cls.own_leave = cls._create_leave(cls.approver_employee, date(2026, 7, 6))
        cls.waiting_leave = cls._create_leave(cls.owner_employee, date(2026, 7, 7))
        cls.unrelated_leave = cls._create_leave(cls.other_employee, date(2026, 7, 8))
        leave_ids = (
            cls.own_leave | cls.waiting_leave | cls.unrelated_leave
        ).ids
        cls.env.cr.execute(
            """
            DELETE FROM hr_leave_approval_actionable_user_rel
            WHERE leave_id IN %s
            """,
            [tuple(leave_ids)],
        )
        cls.env.cr.execute(
            """
            INSERT INTO hr_leave_approval_actionable_user_rel (leave_id, user_id)
            VALUES (%s, %s)
            """,
            [cls.waiting_leave.id, cls.approver.id],
        )
        cls.env.cr.execute(
            """
            INSERT INTO hr_leave_approval_actionable_user_rel (leave_id, user_id)
            VALUES (%s, %s)
            """,
            [cls.waiting_leave.id, cls.limited_approver.id],
        )
        cls.env["hr.leave.responsible.approval"].sudo().create(
            {
                "leave_id": cls.unrelated_leave.id,
                "user_id": cls.limited_approver.id,
                "sequence": 1,
                "state": "approved",
            }
        )
        (cls.own_leave | cls.waiting_leave | cls.unrelated_leave).invalidate_recordset(
            ["approval_actionable_user_ids", "responsible_approval_line_ids"]
        )

    @classmethod
    def _create_leave(cls, employee, request_date):
        return (
            cls.env["hr.leave"]
            .sudo()
            .with_context(leave_fast_create=True)
            .create(
                {
                    "name": "Visibility test",
                    "employee_id": employee.id,
                    "holiday_status_id": cls.leave_type.id,
                    "request_date_from": request_date,
                    "request_date_to": request_date,
                }
            )
        )

    def test_officer_manage_all_requests_keeps_full_visibility(self):
        visible = self.env["hr.leave"].with_user(self.approver).search(
            [
                (
                    "id",
                    "in",
                    [
                        self.own_leave.id,
                        self.waiting_leave.id,
                        self.unrelated_leave.id,
                    ],
                )
            ]
        )

        self.assertEqual(
            set(visible.ids),
            {self.own_leave.id, self.waiting_leave.id, self.unrelated_leave.id},
        )

    def test_non_officer_approver_sees_actionable_and_participated_requests(self):
        visible = self.env["hr.leave"].with_user(self.limited_approver).search(
            [
                (
                    "id",
                    "in",
                    [
                        self.own_leave.id,
                        self.waiting_leave.id,
                        self.unrelated_leave.id,
                    ],
                )
            ]
        )

        self.assertEqual(
            set(visible.ids),
            {self.waiting_leave.id, self.unrelated_leave.id},
        )

    def test_standard_noupdate_rules_preserve_officer_access(self):
        def normalized_domain(xmlid):
            return " ".join(self.env.ref(xmlid).domain_force.split())

        actionable = "[('approval_actionable_user_ids', 'in', [user.id])]"
        officer_update = (
            "[ '|', '&', ('employee_id.user_id', '=', user.id), "
            "('state', '!=', 'validate'), '|', "
            "('employee_id.user_id', '!=', user.id), "
            "('employee_id.user_id', '=', False) ]"
        )
        for xmlid in (
            "hr_holidays.hr_leave_rule_responsible_read",
            "hr_holidays.hr_leave_rule_responsible_update",
        ):
            self.assertEqual(normalized_domain(xmlid), actionable)
        self.assertEqual(
            normalized_domain("hr_holidays.hr_leave_rule_user_read"),
            "[(1, '=', 1)]",
        )
        self.assertEqual(
            normalized_domain("hr_holidays.hr_leave_rule_officer_update"),
            officer_update,
        )

    def test_non_officer_approver_cannot_write_unrelated_request(self):
        with self.assertRaises(AccessError):
            self.unrelated_leave.with_user(self.limited_approver).write(
                {"name": "Unauthorized update"}
            )

    def test_time_off_administrator_keeps_full_visibility(self):
        administrator = new_test_user(
            self.env,
            login="time-off-visibility-administrator",
            groups="hr_holidays.group_hr_holidays_manager",
        )
        visible = self.env["hr.leave"].with_user(administrator).search(
            [
                (
                    "id",
                    "in",
                    [
                        self.own_leave.id,
                        self.waiting_leave.id,
                        self.unrelated_leave.id,
                    ],
                )
            ]
        )

        self.assertEqual(
            set(visible.ids),
            {self.own_leave.id, self.waiting_leave.id, self.unrelated_leave.id},
        )
