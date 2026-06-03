# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

from odoo.addons.hr_job_title_vn.models.hr_version import JOB_TITLE_SELECTION

# Chức danh từ trưởng nhóm trở lên — dùng làm “cấp dừng” skip / nhắc lại.
_MAX_SKIP_JOB_TITLE_MIN_KEY = "trưởng nhóm"
MAX_SKIP_JOB_TITLE_SELECTION = []
_include = False
for _key, _label in JOB_TITLE_SELECTION:
    if _key == _MAX_SKIP_JOB_TITLE_MIN_KEY:
        _include = True
    if _include:
        MAX_SKIP_JOB_TITLE_SELECTION.append((_key, _label))
if not MAX_SKIP_JOB_TITLE_SELECTION:
    MAX_SKIP_JOB_TITLE_SELECTION = [
        ("trưởng bộ phận", "Trưởng bộ phận"),
        ("trưởng phòng", "Trưởng phòng"),
        ("giám đốc", "Giám đốc"),
    ]

_DEFAULT_MAX_SKIP_JOB_TITLE = "trưởng bộ phận"


class HrLeaveOdoobotNotifyConfig(models.Model):
    _name = "hr.leave.odoobot.notify.config"
    _description = "Time Off OdooBot Notification Settings"
    _rec_name = "company_id"

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    remind_interval_hours = fields.Float(
        string="Repeat interval (hours)",
        default=2.0,
        help="Re-send OdooBot approval reminder to the current approver after this many hours.",
    )
    skip_level_hours = fields.Float(
        string="Skip level after (hours)",
        default=2.0,
        help="In sequential responsible approval, auto-skip the current approver after this many hours.",
    )
    max_skip_job_title = fields.Selection(
        selection=MAX_SKIP_JOB_TITLE_SELECTION,
        string="Maximum job title that can be auto-skipped",
        default=_DEFAULT_MAX_SKIP_JOB_TITLE,
        required=True,
        help=(
            "Approvers at this job title or higher are no longer auto-skipped; "
            "OdooBot only sends repeat reminders until they approve or refuse."
        ),
    )

    _company_unique = models.Constraint(
        "unique (company_id)",
        "Each company can only have one OdooBot notification configuration.",
    )

    @api.constrains("remind_interval_hours", "skip_level_hours", "max_skip_job_title")
    def _check_values(self):
        valid_keys = {key for key, _label in MAX_SKIP_JOB_TITLE_SELECTION}
        for config in self:
            if config.remind_interval_hours < 0:
                raise ValidationError(_("Thời gian nhắc lại phải ≥ 0 (0 = tắt nhắc lại)."))
            if config.skip_level_hours <= 0:
                raise ValidationError(_("Thời gian bỏ qua cấp phải lớn hơn 0."))
            if config.max_skip_job_title not in valid_keys:
                raise ValidationError(_("Chức danh dừng skip không hợp lệ."))

    @api.model
    def _get_for_company(self, company=None):
        company = company or self.env.company
        if not company:
            return self.browse()
        config = self.search([("company_id", "=", company.id)], limit=1)
        if not config:
            config = self.create(
                {
                    "company_id": company.id,
                    "remind_interval_hours": 2.0,
                    "skip_level_hours": 2.0,
                    "max_skip_job_title": _DEFAULT_MAX_SKIP_JOB_TITLE,
                }
            )
        return config

    def action_open_config(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Thông báo odoobot"),
            "res_model": self._name,
            "view_mode": "form",
            "res_id": self.id,
            "target": "current",
        }

    @api.model
    def action_open_company_config(self):
        config = self._get_for_company()
        return config.action_open_config()
