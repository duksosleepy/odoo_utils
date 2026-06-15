import json
from datetime import date

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStoreRegionExport(TransactionCase):
    def test_all_year_filter_sets_calendar_year_bounds(self):
        wizard = self.env["hr.leave.matrix.export.wizard"].new(
            {
                "year": 2027,
                "regional_date_filter": "all_year",
            }
        )

        wizard._onchange_regional_date_filter()

        self.assertEqual(wizard.regional_date_from, date(2027, 1, 1))
        self.assertEqual(wizard.regional_date_to, date(2027, 12, 31))

    def test_regional_domain_includes_date_and_employee_filters(self):
        base_domain = [("state", "=", "validate")]
        wizard = self.env["hr.leave.matrix.export.wizard"].create(
            {
                "year": 2026,
                "month": 1,
                "regional_date_filter": "custom",
                "regional_date_from": date(2026, 1, 1),
                "regional_date_to": date(2026, 12, 31),
                "regional_mien": "Nam",
                "regional_employee_hrm_id": " HRM001 ",
                "regional_attendance_code": " MCC001 ",
                "domain_json": json.dumps(base_domain),
            }
        )

        domain = wizard._regional_store_leave_domain()

        self.assertIn(("state", "=", "validate"), domain)
        self.assertIn(("request_date_from", "<=", date(2026, 12, 31)), domain)
        self.assertIn(("request_date_to", ">=", date(2026, 1, 1)), domain)
        self.assertIn(("employee_id.id_hrm", "=ilike", "HRM001"), domain)
        self.assertIn(
            ("employee_id.ma_cham_cong", "=ilike", "MCC001"),
            domain,
        )

    def test_regional_date_range_rejects_reversed_dates(self):
        with self.assertRaises(UserError):
            self.env["hr.leave.matrix.export.wizard"].create(
                {
                    "year": 2026,
                    "month": 1,
                    "regional_date_filter": "custom",
                    "regional_date_from": date(2026, 12, 31),
                    "regional_date_to": date(2026, 1, 1),
                    "regional_mien": "Bắc",
                }
            )
