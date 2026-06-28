# -*- coding: utf-8 -*-

import logging

from odoo import SUPERUSER_ID, models
from odoo.http import request

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    def authenticate(self, credential, user_agent_env):
        auth_info = super().authenticate(credential, user_agent_env=user_agent_env)
        if auth_info and auth_info.get("uid") and request:
            try:
                with self.env.cr.savepoint():
                    self.env(user=SUPERUSER_ID)["lug.user.session"]._register_login(
                        auth_info["uid"]
                    )
            except Exception:
                _logger.exception("Lug Security: failed to register login session")
        return auth_info
