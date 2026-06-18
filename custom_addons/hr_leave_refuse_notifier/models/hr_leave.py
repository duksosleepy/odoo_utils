# -*- coding: utf-8 -*-
from odoo import _, models


class HrLeave(models.Model):
    _inherit = "hr.leave"

    def _notify_manager(self):
        result = super()._notify_manager()
        self._notify_refuse_ticket_notifier()
        return result

    def _notify_refuse_ticket_notifier(self):
        for leave in self:
            employee = leave.holiday_status_id.refuse_notify_employee_id
            if not employee or not employee.user_id:
                continue
            leave.message_notify(
                partner_ids=employee.user_id.partner_id.ids,
                subject=_("Time Off Request Refused"),
                body=_(
                    "%(leave_name)s has been refused.",
                    leave_name=leave.display_name,
                ),
                email_layout_xmlid="mail.mail_notification_layout",
            )
