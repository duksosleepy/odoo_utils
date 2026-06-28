# -*- coding: utf-8 -*-

from odoo import api, fields, models

from .lug_request_utils import device_category_from_meta


class LugDevice(models.Model):
    _name = "lug.device"
    _description = "Lug Security Device"
    _order = "last_login desc, id desc"
    _rec_name = "device_name"

    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        ondelete="cascade",
        index=True,
    )
    device_name = fields.Char(string="Thiết bị", required=True, index=True)
    serial_number = fields.Char(string="Serial")
    mac_address = fields.Char(string="MAC Address")
    browser = fields.Char(string="Browser")
    os = fields.Char(string="OS")
    first_login = fields.Datetime(string="Lần đăng nhập đầu", required=True)
    last_login = fields.Datetime(string="Lần đăng nhập cuối", required=True, index=True)
    session_count = fields.Integer(
        string="Số phiên",
        compute="_compute_session_count",
    )

    _user_device_uniq = models.Constraint(
        "UNIQUE(user_id, device_name)",
        "Thiết bị đã tồn tại cho user này.",
    )

    @api.depends("user_id")
    def _compute_session_count(self):
        if not self.ids:
            return
        counts = dict(
            self.env["lug.user.session"]._read_group(
                [("device_id", "in", self.ids)],
                ["device_id"],
                ["__count"],
            )
        )
        for device in self:
            device.session_count = counts.get(device, 0)

    @api.model
    def _touch_from_request(self, user, meta):
        """Register or update device from login / heartbeat metadata."""
        device_name = meta.get("device_name") or "PC"
        now = fields.Datetime.now()
        device = self.sudo().search(
            [("user_id", "=", user.id), ("device_name", "=", device_name)],
            limit=1,
        )
        vals = {
            "browser": meta.get("browser"),
            "os": meta.get("os"),
            "last_login": now,
        }
        if meta.get("serial_number"):
            vals["serial_number"] = meta["serial_number"]
        if meta.get("mac_address"):
            vals["mac_address"] = meta["mac_address"]
        if device:
            device.write(vals)
            return device
        vals.update({
            "user_id": user.id,
            "device_name": device_name,
            "first_login": now,
        })
        return self.sudo().create(vals)

    @api.model
    def _device_name_from_meta(self, meta):
        return device_category_from_meta(meta)
