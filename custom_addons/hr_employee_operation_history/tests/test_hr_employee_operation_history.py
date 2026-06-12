# -*- coding: utf-8 -*-

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestHrEmployeeOperationHistory(TransactionCase):

    def _create_test_employee(self, suffix):
        return self.env['hr.employee'].create({
            'name': f'Operation Log Test Employee {suffix}',
            'id_hrm': f'OPLOG-{suffix}',
        })

    def test_create_logs_operation(self):
        employee = self._create_test_employee('CREATE')
        logs = employee.operation_log_ids.filtered(lambda log: log.operation == 'create')
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs.user_id, self.env.user)
        self.assertTrue(logs.change_line_ids)

    def test_write_logs_field_change(self):
        employee = self._create_test_employee('WRITE')
        before_count = len(employee.operation_log_ids)
        employee.write({'id_hrm': 'OPLOG-WRITE-NEW'})
        self.assertEqual(len(employee.operation_log_ids), before_count + 1)
        write_log = employee.operation_log_ids.filtered(
            lambda log: log.operation == 'write'
            and log.change_line_ids.filtered(lambda line: line.field_name == 'id_hrm')
        )
        self.assertEqual(len(write_log), 1)
        id_hrm_line = write_log.change_line_ids.filtered(
            lambda line: line.field_name == 'id_hrm'
        )
        self.assertEqual(len(id_hrm_line), 1)
        self.assertEqual(id_hrm_line.old_value, 'OPLOG-WRITE')
        self.assertEqual(id_hrm_line.new_value, 'OPLOG-WRITE-NEW')
        self.assertIn('OPLOG-WRITE', write_log.change_summary)
        self.assertIn('OPLOG-WRITE-NEW', write_log.change_summary)

    def test_panel_data_returns_logs(self):
        employee = self._create_test_employee('PANEL')
        employee.write({'id_hrm': 'OPLOG-PANEL-NEW'})
        data = employee.get_operation_history_panel_data()
        self.assertGreaterEqual(len(data), 2)
        write_entries = [row for row in data if row['change_summary']]
        self.assertTrue(write_entries)
        self.assertIn('OPLOG-PANEL-NEW', write_entries[0]['change_summary'])

    def test_unlink_logs_before_delete(self):
        employee = self._create_test_employee('DELETE')
        employee_id = employee.id
        employee_name = employee.name
        employee.unlink()
        delete_log = self.env['hr.employee.operation.log'].search([
            ('employee_ref_id', '=', employee_id),
            ('operation', '=', 'unlink'),
        ], limit=1)
        self.assertTrue(delete_log)
        self.assertEqual(delete_log.employee_name, employee_name)
        self.assertEqual(delete_log.user_id, self.env.user)
