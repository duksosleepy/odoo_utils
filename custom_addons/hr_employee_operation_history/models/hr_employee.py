# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.misc import format_datetime
from odoo.tools.translate import _

_OPERATION_LOG_SKIP_FIELDS = frozenset({
    '__last_update',
    'activity_date_deadline',
    'activity_exception_decoration',
    'activity_exception_icon',
    'activity_ids',
    'activity_state',
    'activity_summary',
    'activity_type_icon',
    'activity_type_id',
    'activity_user_id',
    'create_date',
    'create_uid',
    'display_name',
    'last_modified_date',
    'last_modified_uid',
    'message_attachment_count',
    'message_follower_ids',
    'message_has_error',
    'message_has_error_counter',
    'message_has_sms_error',
    'message_ids',
    'message_is_follower',
    'message_needaction',
    'message_needaction_counter',
    'message_partner_ids',
    'operation_log_count',
    'operation_log_ids',
    'website_message_ids',
    'write_date',
    'write_uid',
})


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    operation_log_ids = fields.One2many(
        'hr.employee.operation.log',
        'employee_id',
        string='Operation History',
        groups='hr.group_hr_user',
    )
    operation_log_count = fields.Integer(
        string='Operation History Count',
        compute='_compute_operation_log_count',
        groups='hr.group_hr_user',
    )

    @api.depends('operation_log_ids')
    def _compute_operation_log_count(self):
        for employee in self:
            employee.operation_log_count = len(employee.operation_log_ids)

    def _should_skip_operation_log(self):
        return (
            self.env.context.get('skip_employee_operation_log')
            or self.env.context.get('install_mode')
            or self.env.context.get('module')
        )

    def _operation_log_field_label(self, field_name):
        field = self._fields.get(field_name)
        return field.string if field else field_name

    def _operation_log_format_value(self, field_name, value):
        field = self._fields.get(field_name)
        if not field:
            return str(value or '')
        if value in (False, None, ''):
            return ''
        if field.type == 'many2one':
            return self.env[field.comodel_name].browse(value).display_name
        if field.type == 'many2many':
            return ', '.join(self.env[field.comodel_name].browse(value).mapped('display_name'))
        if field.type == 'one2many':
            return ', '.join(self.env[field.comodel_name].browse(value).mapped('display_name'))
        if field.type == 'selection':
            return dict(field.selection).get(value, value)
        if field.type == 'boolean':
            return _('Yes') if value else _('No')
        if field.type == 'date':
            if isinstance(value, str):
                return value
            return fields.Date.to_string(value)
        if field.type == 'datetime':
            if isinstance(value, str):
                return value
            return fields.Datetime.to_string(value)
        return str(value)

    def _operation_log_format_record_value(self, field_name):
        self.ensure_one()
        field = self._fields.get(field_name)
        if not field or not self._has_field_access(field, 'read'):
            return ''
        value = self[field_name]
        if value in (False, None, ''):
            return ''
        if field.type == 'many2one':
            return value.display_name
        if field.type in ('many2many', 'one2many'):
            return ', '.join(value.mapped('display_name'))
        if field.type == 'selection':
            return dict(field.selection).get(value, value)
        if field.type == 'boolean':
            return _('Yes') if value else _('No')
        if field.type == 'date':
            return fields.Date.to_string(value)
        if field.type == 'datetime':
            return fields.Datetime.to_string(value)
        return str(value)

    def _operation_log_is_loggable_field(self, field_name):
        field = self._fields.get(field_name)
        if not field or field_name in _OPERATION_LOG_SKIP_FIELDS:
            return False
        if not self._has_field_access(field, 'read'):
            return False
        if field.related and not field.store:
            return False
        if field.compute and not field.store:
            return False
        if field.type in ('binary', 'html'):
            return False
        return True

    def _operation_log_prepare_change_lines(self, vals):
        self.ensure_one()
        lines = []
        for field_name, new_raw in vals.items():
            if not self._operation_log_is_loggable_field(field_name):
                continue
            old_display = self._operation_log_format_record_value(field_name)
            new_display = self._operation_log_format_value(field_name, new_raw)
            if old_display == new_display:
                continue
            lines.append({
                'field_name': field_name,
                'field_label': self._operation_log_field_label(field_name),
                'old_value': old_display,
                'new_value': new_display,
            })
        return lines

    def _operation_log_prepare_create_lines(self, vals):
        lines = []
        for field_name, new_raw in vals.items():
            if not self._operation_log_is_loggable_field(field_name):
                continue
            new_display = self._operation_log_format_value(field_name, new_raw)
            if not new_display:
                continue
            lines.append({
                'field_name': field_name,
                'field_label': self._operation_log_field_label(field_name),
                'old_value': '',
                'new_value': new_display,
            })
        return lines

    def _create_operation_log(self, operation, change_lines=None):
        self.ensure_one()
        if self._should_skip_operation_log():
            return self.env['hr.employee.operation.log']
        Log = self.env['hr.employee.operation.log'].sudo()
        values = {
            'employee_id': self.id,
            'employee_ref_id': self.id,
            'employee_name': self.name,
            'user_id': self.env.uid,
            'operation': operation,
            'operation_date': fields.Datetime.now(),
        }
        if change_lines:
            values['change_line_ids'] = [(0, 0, line) for line in change_lines]
        return Log.create(values)

    @api.model_create_multi
    def create(self, vals_list):
        employees = super().create(vals_list)
        if self._should_skip_operation_log():
            return employees
        for employee, vals in zip(employees, vals_list):
            change_lines = employee._operation_log_prepare_create_lines(vals)
            employee._create_operation_log('create', change_lines or None)
        return employees

    def write(self, vals):
        if self._should_skip_operation_log() or not vals:
            return super().write(vals)
        pending_logs = []
        for employee in self:
            change_lines = employee._operation_log_prepare_change_lines(vals)
            if change_lines:
                pending_logs.append((employee, change_lines))
        result = super().write(vals)
        for employee, change_lines in pending_logs:
            employee._create_operation_log('write', change_lines)
        return result

    def unlink(self):
        if not self._should_skip_operation_log():
            Log = self.env['hr.employee.operation.log'].sudo()
            now = fields.Datetime.now()
            for employee in self:
                Log.create({
                    'employee_id': employee.id,
                    'employee_ref_id': employee.id,
                    'employee_name': employee.name,
                    'user_id': self.env.uid,
                    'operation': 'unlink',
                    'operation_date': now,
                })
        return super().unlink()

    def get_operation_history_panel_data(self):
        self.ensure_one()
        if not self.env.user.has_group('hr.group_hr_user'):
            return []
        Log = self.env['hr.employee.operation.log']
        operation_labels = dict(Log._fields['operation'].selection)
        logs = Log.search(
            [('employee_id', '=', self.id)],
            order='operation_date desc, id desc',
        )
        panel_data = []
        for log in logs:
            panel_data.append({
                'id': log.id,
                'operation_date': format_datetime(self.env, log.operation_date),
                'operation': operation_labels.get(log.operation, log.operation),
                'user_name': log.user_id.display_name,
                'user_id': log.user_id.id,
                'change_summary': log.change_summary or '',
                'change_count': log.change_count,
            })
        return panel_data

    def action_view_operation_history(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Operation History'),
            'res_model': 'hr.employee.operation.log',
            'view_mode': 'list,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {
                'default_employee_id': self.id,
                'default_employee_name': self.name,
                'search_default_employee_id': self.id,
            },
        }
