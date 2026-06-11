from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMonthlyLeaveAppointmentBonus(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.job_nhom_truong = cls.env["hr.job"].create({"name": "Nhóm trưởng"})
        cls.today = fields.Date.today()
        cls.join_date = cls.today - relativedelta(years=4, days=1)

    def _create_employee(self, **extra):
        values = {
            "name": "Tenure Bonus Employee",
            "mien": "Nam",
            "job_id": self.job_nhom_truong.id,
            "ngay_vao_lam": self.join_date,
            "tong_so_phep": 0.0,
        }
        values.update(extra)
        return self.env["hr.employee"].create(values)

    def test_appointment_before_day_15_grants_bonus_on_save(self):
        employee = self._create_employee()

        employee.write({"ngay_bo_nhiem": date(2026, 3, 10)})

        self.assertEqual(employee.tong_so_phep, 1.0)

    def test_appointment_on_day_15_blocks_bonus(self):
        employee = self._create_employee()

        employee.write({"ngay_bo_nhiem": date(2026, 3, 15)})

        self.assertEqual(employee.tong_so_phep, 0.0)

    def test_missing_appointment_blocks_bonus(self):
        employee = self._create_employee()

        employee.with_context(monthly_leave_bonus_date=date(2026, 6, 1)).write(
            {"tong_so_phep": 1.0}
        )

        self.assertEqual(employee.tong_so_phep, 0.0)

    def test_under_four_years_blocks_bonus(self):
        employee = self._create_employee(
            ngay_vao_lam=self.today - relativedelta(years=3),
        )

        employee.write({"ngay_bo_nhiem": date(2026, 3, 10)})

        self.assertEqual(employee.tong_so_phep, 0.0)

    def test_cron_applies_bonus_for_eligible_employee(self):
        employee = self._create_employee(
            ngay_vao_lam=date(2020, 1, 1),
            ngay_bo_nhiem=date(2020, 1, 5),
        )

        self.env["hr.employee"].cron_apply_monthly_leave_bonus()

        self.assertEqual(employee.tong_so_phep, 1.0)
