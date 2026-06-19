# -*- coding: utf-8 -*-
import logging

from odoo import _, models

_logger = logging.getLogger(__name__)


class HrLeave(models.Model):
    _inherit = "hr.leave"

    def _notify_manager(self):
        result = super()._notify_manager()
        try:
            self._notify_refuse_ticket_notifier()
        except Exception:
            _logger.exception("hr_leave_refuse_notifier: failed to notify refuse ticket notifier")
        return result

    def _notify_refuse_ticket_notifier(self):
        refuser = self.env.user.display_name
        odoobot_partner = self.env.ref("base.partner_root", raise_if_not_found=False)
        if not odoobot_partner:
            _logger.warning("hr_leave_refuse_notifier: mail.partner_odoobot not found")
            return
        for leave in self:
            employee = leave.holiday_status_id.refuse_notify_employee_id
            if not employee or not employee.user_id:
                _logger.info(
                    "hr_leave_refuse_notifier: skip leave_id=%s employee=%s has_user=%s",
                    leave.id,
                    employee.id if employee else None,
                    bool(employee.user_id) if employee else False,
                )
                continue
            _logger.info(
                "hr_leave_refuse_notifier: notifying employee_id=%s (%s) for leave_id=%s",
                employee.id,
                employee.user_id.login,
                leave.id,
            )
            body = _(
                "%(leave_name)s has been refused by %(refuser)s.",
                leave_name=leave.display_name,
                refuser=refuser,
            )
            try:
                chat = (
                    self.env["discuss.channel"]
                    .sudo()
                    .with_user(employee.user_id)
                    ._get_or_create_chat([odoobot_partner.id], pin=True)
                )
                chat.with_user(employee.user_id).sudo().message_post(
                    body=body,
                    message_type="comment",
                    subtype_xmlid="mail.mt_comment",
                    author_id=odoobot_partner.id,
                )
            except Exception:
                _logger.exception(
                    "hr_leave_refuse_notifier: OdooBot DM failed leave_id=%s employee_id=%s",
                    leave.id,
                    employee.id,
                )
