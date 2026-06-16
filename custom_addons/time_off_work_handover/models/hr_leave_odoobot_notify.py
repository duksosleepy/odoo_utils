# -*- coding: utf-8 -*-

import logging

from markupsafe import Markup, escape

from odoo import _, fields, models
from odoo.addons.time_off_work_handover import constants as handover_constants

_logger = logging.getLogger(__name__)

_HANDOVER_ACTIVE_STATES = handover_constants.HANDOVER_ACTIVE_STATES


class HrLeaveHandoverOdoobotNotify(models.Model):
    _inherit = "hr.leave"

    def _handover_rule_user(self):
        """User whose job title drives skip/remind rules for the active handover step."""
        self.ensure_one()
        if self.handover_escalated and self.handover_escalation_user_id:
            return self.handover_escalation_user_id
        pending = self.handover_acceptance_ids.filtered(
            lambda line: line.state == "pending"
            and line.employee_id in self.handover_employee_ids
        )
        if pending:
            employee = pending[0].employee_id
            return employee.user_id if employee else False
        return self.employee_id.user_id

    def _handover_escalation_after_hours(self):
        self.ensure_one()
        user = self._handover_rule_user()
        if user:
            hours = self._odoobot_skip_hours_for_user(user, "handover")
            if hours:
                return hours
        return super()._handover_escalation_after_hours()

    def _handover_is_max_escalation_reached(self):
        self.ensure_one()
        if super()._handover_is_max_escalation_reached():
            return True
        user = self.handover_escalation_user_id
        if user and self._odoobot_blocks_auto_skip_for_user(user, "handover"):
            return True
        return False

    def _notify_handover_scheduled_remind_via_bot(self, employees):
        """Scheduled alarm: reminder + button to open handover acceptance."""
        self.ensure_one()
        if not employees:
            return
        notify_leave = self._get_handover_bot_notify_leave()
        requester_name = (
            notify_leave.employee_id.name
            or notify_leave.employee_id.display_name
            or notify_leave.display_name
        )
        group = (
            notify_leave._get_split_group_leaves_all()
            if notify_leave.split_group_id
            else notify_leave
        )
        date_from, date_to = notify_leave._get_handover_bot_period_from_to(group)
        intro = Markup(
            _(
                "Bạn có đơn xin nghỉ cần bàn giao việc của <b>{requester}</b> "
                "vào ngày <b>{date_from}</b> đến ngày <b>{date_to}</b> "
                "chưa giải quyết được, hãy cố gắng giải quyết nhé.<br/><br/>"
            )
        ).format(
            requester=escape(requester_name),
            date_from=date_from,
            date_to=date_to,
        )
        button_html = notify_leave._notify_discuss_leave_open_button_markup(
            _("Bàn giao việc"),
            discuss_link_type="handover",
        )
        body = intro + button_html
        bot_xmlid = "business_discuss_bots.user_bot_handover"
        for recipient in employees:
            user = recipient.user_id
            if not user or not user.partner_id:
                continue
            notify_leave._post_odoobot_bot_discuss_message(bot_xmlid, user, body)

    def cron_remind_handover_odoobot(self):
        """Re-send handover OdooBot at configured alarm times for pending recipients."""
        leaves = self.sudo().search(
            [
                ("state", "in", _HANDOVER_ACTIVE_STATES),
                ("handover_employee_ids", "!=", False),
                ("skip_work_handover", "=", False),
            ]
        )
        for leave in leaves:
            try:
                if leave.handover_escalated:
                    user = leave.handover_escalation_user_id
                    if not user:
                        continue
                    rule = leave._odoobot_notify_rule_for_user(user, "handover")
                    slot_key = leave._odoobot_scheduled_remind_due(
                        rule, "handover_last_odoobot_remind_slot"
                    )
                    if not slot_key:
                        continue
                    esc_employee = leave._handover_employee_for_assigner_user(user)
                    if esc_employee:
                        leave._notify_handover_scheduled_remind_via_bot(esc_employee)
                    leave._odoobot_mark_scheduled_remind_sent("handover", slot_key)
                    continue
                pending_employees = leave.handover_acceptance_ids.filtered(
                    lambda line: line.state == "pending"
                    and line.employee_id in leave.handover_employee_ids
                ).mapped("employee_id")
                if not pending_employees:
                    continue
                notify_leave = leave._get_handover_bot_notify_leave()
                for employee in pending_employees:
                    rule = notify_leave._odoobot_notify_rule_for_employee(
                        employee, "handover"
                    )
                    slot_key = (
                        rule.sudo()._matching_remind_slot_key() if rule else False
                    )
                    if not slot_key:
                        continue
                    employee_slot = "%s|e%s" % (slot_key, employee.id)
                    if notify_leave.handover_last_odoobot_remind_slot == employee_slot:
                        continue
                    notify_leave._notify_handover_scheduled_remind_via_bot(
                        employee
                    )
                    notify_leave._odoobot_mark_scheduled_remind_sent(
                        "handover", employee_slot
                    )
            except Exception:
                _logger.exception(
                    "time_off_work_handover: handover OdooBot remind failed leave_id=%s",
                    leave.id,
                )
