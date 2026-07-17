# -*- coding: utf-8 -*-

import logging

from markupsafe import Markup, escape

from odoo import _, models

_logger = logging.getLogger(__name__)


class LugTaskNotify(models.AbstractModel):
    _name = "lug.task.notify.mixin"
    _description = "Thông báo Discuss cho giao việc"

    def _lug_task_bot_user(self):
        bot = self.env.ref("lug_task_assignment.user_bot_task", raise_if_not_found=False)
        return bot if bot and bot.active else False

    def _lug_task_send_bot_message(self, user, body_html):
        if not user or not user.partner_id:
            return False
        bot = self._lug_task_bot_user()
        if not bot:
            return False
        try:
            channel = (
                self.env["discuss.channel"]
                .with_user(bot)
                .sudo()
                ._get_or_create_chat([user.partner_id.id], pin=True)
            )
            channel.with_user(bot).sudo().message_post(
                author_id=bot.partner_id.id,
                body=body_html,
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
            )
        except Exception:
            _logger.exception("lug_task_assignment: bot message failed")
            return False
        return True

    def _lug_task_notify_assignment(self, task):
        user = task.assigned_to_id.user_id if task.assigned_to_id else False
        if not user:
            return
        body = Markup(
            _(
                "Bạn được giao việc <b>%(title)s</b> (%(code)s) "
                "bởi <b>%(assigner)s</b>. Hạn: <b>%(due)s</b>."
            )
        ) % {
            "title": escape(task.title),
            "code": escape(task.task_code or ""),
            "assigner": escape(task.assigned_by_id.name or ""),
            "due": task.due_date.strftime("%d/%m/%Y %H:%M") if task.due_date else "-",
        }
        self._lug_task_send_bot_message(user, body)

    def _lug_task_notify_review_request(self, task):
        reviewer = task.reviewer_id.user_id if task.reviewer_id else False
        if not reviewer:
            manager = task.assigned_to_id.parent_id if task.assigned_to_id else False
            reviewer = manager.user_id if manager else False
        if not reviewer:
            return
        body = Markup(
            _("Việc <b>%(title)s</b> (%(code)s) đang chờ bạn duyệt kết quả.")
        ) % {"title": escape(task.title), "code": escape(task.task_code or "")}
        self._lug_task_send_bot_message(reviewer, body)

    def _lug_task_notify_overdue(self, task):
        partners = []
        if task.assigned_to_id and task.assigned_to_id.parent_id:
            user = task.assigned_to_id.parent_id.user_id
            if user:
                body = Markup(
                    _("<span style='color:red'>QUÁ HẠN</span>: %(title)s (%(code)s)")
                ) % {"title": escape(task.title), "code": escape(task.task_code or "")}
                self._lug_task_send_bot_message(user, body)
                partners.append(user)
        if task.department_id and task.department_id.manager_id:
            director_user = task.department_id.manager_id.user_id
            if director_user and director_user not in partners:
                body = Markup(
                    _("<span style='color:red'>Leo thang quá hạn</span>: %(title)s")
                ) % {"title": escape(task.title)}
                self._lug_task_send_bot_message(director_user, body)
