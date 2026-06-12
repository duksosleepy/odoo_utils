# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.translate import _


class HrEmployeeOperationLog(models.Model):
    _name = 'hr.employee.operation.log'
    _description = 'Employee Operation Log'
    _order = 'operation_date desc, id desc'
    _rec_name = 'display_name'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        ondelete='set null',
        index=True,
    )
    employee_ref_id = fields.Integer(
        string='Employee Reference',
        index=True,
        readonly=True,
    )
    employee_name = fields.Char(string='Employee Name', required=True, index=True)
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        index=True,
        default=lambda self: self.env.user,
    )
    operation = fields.Selection(
        selection=[
            ('create', 'Create'),
            ('write', 'Update'),
            ('unlink', 'Delete'),
        ],
        string='Operation',
        required=True,
        index=True,
    )
    operation_date = fields.Datetime(
        string='Operation Date',
        required=True,
        default=fields.Datetime.now,
        index=True,
    )
    change_line_ids = fields.One2many(
        'hr.employee.operation.log.line',
        'log_id',
        string='Changes',
    )
    change_count = fields.Integer(
        string='Change Count',
        compute='_compute_change_count',
        store=True,
        readonly=True,
    )
    change_summary = fields.Text(
        string='Change Summary',
        compute='_compute_change_summary',
        store=True,
        readonly=True,
    )
    display_name = fields.Char(compute='_compute_display_name')

    @api.depends('change_line_ids')
    def _compute_change_count(self):
        for log in self:
            log.change_count = len(log.change_line_ids)

    @api.depends(
        'change_line_ids.field_label',
        'change_line_ids.old_value',
        'change_line_ids.new_value',
    )
    def _compute_change_summary(self):
        for log in self:
            log.change_summary = self._format_change_summary(log.change_line_ids)

    @api.model
    def _format_change_summary(self, change_lines):
        empty = _('Empty')
        parts = []
        for line in change_lines:
            old = (line.get('old_value') if isinstance(line, dict) else line.old_value) or empty
            new = (line.get('new_value') if isinstance(line, dict) else line.new_value) or empty
            label = line.get('field_label') if isinstance(line, dict) else line.field_label
            parts.append(f'{label}: {old} → {new}')
        return '\n'.join(parts)

    def _compute_display_name(self):
        operation_labels = dict(self._fields['operation'].selection)
        for log in self:
            label = operation_labels.get(log.operation, log.operation)
            log.display_name = f"{log.employee_name} - {label}"

    @api.model
    def _backfill_change_summaries(self):
        logs = self.search([('change_line_ids', '!=', False)])
        if logs:
            logs._recompute_recordset(['change_count', 'change_summary'])


class HrEmployeeOperationLogLine(models.Model):
    _name = 'hr.employee.operation.log.line'
    _description = 'Employee Operation Log Line'
    _order = 'id'

    log_id = fields.Many2one(
        'hr.employee.operation.log',
        string='Log',
        required=True,
        ondelete='cascade',
        index=True,
    )
    field_name = fields.Char(string='Field Name')
    field_label = fields.Char(string='Field Label', required=True)
    old_value = fields.Text(string='Old Value')
    new_value = fields.Text(string='New Value')
