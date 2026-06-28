# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class LugSecurityApi(http.Controller):

    @http.route("/lug/security/heartbeat", type="jsonrpc", auth="user", readonly=False)
    def heartbeat(self):
        return request.env["lug.user.session"]._heartbeat()
