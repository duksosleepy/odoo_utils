from datetime import date, datetime

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestLeaveListDateDisplay(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Leave = cls.env["hr.leave"]
        cls.LeaveType = cls.env["hr.leave.type"]
        cls.employee = cls.env["hr.employee"].create({"name": "Date Display Tester"})
        cls.p1_type = cls.LeaveType.create(
            {
                "name": "Nghỉ phép (P1)",
                "requires_allocation": "no",
                "leave_validation_type": "no_validation",
            }
        )
        cls.hour_type = cls.LeaveType.create(
            {
                "name": "Nghỉ theo giờ (H)",
                "requires_allocation": "no",
                "leave_validation_type": "no_validation",
                "request_unit": "hour",
            }
        )

    def _make_leave(self, leave_type, request_date):
        start_dt = datetime(2026, 7, 10, 8, 0, 0)
        end_dt = datetime(2026, 7, 10, 17, 30, 0)
        return self.Leave.create(
            {
                "name": "Test leave",
                "employee_id": self.employee.id,
                "holiday_status_id": leave_type.id,
                "request_date_from": request_date,
                "request_date_to": request_date,
                "date_from": start_dt,
                "date_to": end_dt,
            }
        )

    def test_p1_list_dates_hide_time(self):
        leave = self._make_leave(self.p1_type, date(2026, 7, 10))
        leave._compute_leave_list_date_display()

        self.assertNotIn("8:00", leave.leave_list_date_from_display)
        self.assertNotIn("17:30", leave.leave_list_date_to_display)
        self.assertIn("10", leave.leave_list_date_from_display)
        self.assertIn("10", leave.leave_list_date_to_display)

    def test_non_p1_p2_o_list_dates_keep_time(self):
        leave = self._make_leave(self.hour_type, date(2026, 7, 10))
        leave._compute_leave_list_date_display()

        self.assertIn("8", leave.leave_list_date_from_display)
        self.assertIn("17", leave.leave_list_date_to_display)
