# -*- coding: utf-8 -*-
"""Inject data-oe-model / data-oe-id on /mail/view links in message bodies.

Discuss + mobile WebKit often fail to follow raw /mail/view hrefs. Stock JS already
opens records from data-oe-* on anchors; these attributes are allow-listed in
html sanitize (see odoo.tools.mail).
"""

import logging
from urllib.parse import parse_qs, urlparse

from lxml import html as lxml_html
from markupsafe import Markup

from odoo import api, models

_logger = logging.getLogger(__name__)


def _inject_mail_view_anchor_attrs(body_html, fallback_model, fallback_res_id):
    """Return new Markup body with data-oe-* on <a href=...mail/view...>, or unchanged."""
    if not body_html or "mail/view" not in body_html:
        return body_html
    body_str = str(body_html)
    if "data-oe-model" in body_str and "data-oe-id" in body_str:
        return body_html
    try:
        root = lxml_html.fromstring(f"<div>{body_str}</div>")
    except (lxml_html.ParserError, ValueError) as e:
        _logger.debug("mail_discuss_mobile_links: skip body parse: %s", e)
        return body_html

    changed = False
    for el in root.iter("a"):
        href = el.get("href") or ""
        if "mail/view" not in href:
            continue
        if el.get("data-oe-model") and el.get("data-oe-id"):
            continue
        model, rid = None, None
        try:
            parsed = urlparse(href)
            q = parse_qs(parsed.query)
            if q.get("model") and q.get("res_id"):
                model = q["model"][0]
                rid = int(q["res_id"][0])
        except (ValueError, TypeError, KeyError):
            pass
        if not model or not rid:
            if fallback_model and fallback_res_id:
                model, rid = fallback_model, int(fallback_res_id)
        if not model or not rid:
            continue
        el.set("data-oe-model", model)
        el.set("data-oe-id", str(int(rid)))
        changed = True

    if not changed:
        return body_html

    inner = root[0]
    out = "".join(
        lxml_html.tostring(child, encoding="unicode", method="html") for child in inner
    )
    return Markup(out)


class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.model
    def _mdl_bulk_inject(self, limit=5000):
        """Gọi sau upgrade module: bổ sung data-oe-* cho tin cũ có /mail/view."""
        domain = [
            ("body", "ilike", "%mail/view%"),
            ("body", "not ilike", "%data-oe-model%"),
        ]
        msgs = self.sudo().search(domain, limit=limit, order="id desc")
        if msgs:
            msgs._mdl_apply_body_link_attrs()

    def _mdl_apply_body_link_attrs(self):
        """Add data-oe-* on mail/view links using URL or message model/res_id."""
        ctx = dict(self.env.context, mdl_skip_link_inject=True)
        for message in self:
            if not message.body:
                continue
            new_body = _inject_mail_view_anchor_attrs(
                message.body,
                message.model,
                message.res_id,
            )
            if str(new_body) == str(message.body):
                continue
            message.with_context(**ctx).write({"body": new_body})

    @api.model_create_multi
    def create(self, vals_list):
        messages = super().create(vals_list)
        if not self.env.context.get("mdl_skip_link_inject"):
            messages._mdl_apply_body_link_attrs()
        return messages

    def write(self, vals):
        if self.env.context.get("mdl_skip_link_inject"):
            return super().write(vals)
        res = super().write(vals)
        if "body" in vals or "model" in vals or "res_id" in vals:
            self._mdl_apply_body_link_attrs()
        return res
