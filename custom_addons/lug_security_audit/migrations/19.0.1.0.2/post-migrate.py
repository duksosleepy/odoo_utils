# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID

from odoo.addons.lug_security_audit.models.lug_request_utils import (
    device_category_from_meta,
    is_usable_client_ip,
)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    Device = env["lug.device"].sudo()
    Session = env["lug.user.session"].sudo()
    valid = {"PC", "Laptop", "Di động"}

    for device in Device.search([]):
        if device.device_name in valid:
            continue
        category = device_category_from_meta({
            "user_agent": device.browser or device.device_name or "",
            "platform": device.os or "",
        })
        duplicate = Device.search([
            ("user_id", "=", device.user_id.id),
            ("device_name", "=", category),
            ("id", "!=", device.id),
        ], limit=1)
        if duplicate:
            Session.search([("device_id", "=", device.id)]).write({"device_id": duplicate.id})
            device.unlink()
        else:
            device.write({"device_name": category})

    for session in Session.search([("ip_address", "!=", False)]):
        if not is_usable_client_ip(session.ip_address):
            session.write({"ip_address": False})
