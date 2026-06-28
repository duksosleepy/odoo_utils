# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID, http
from odoo.addons.web.controllers.session import Session
from odoo.http import request


class LugSecuritySession(Session):

    @http.route()
    def destroy(self):
        self._lug_security_close_session()
        return super().destroy()

    @http.route()
    def logout(self, redirect="/odoo"):
        self._lug_security_close_session()
        return super().logout(redirect=redirect)

    def _lug_security_close_session(self):
        session = getattr(request, "session", None)
        if not session or not session.sid:
            return
        try:
            request.env(user=SUPERUSER_ID)["lug.user.session"]._close_by_session_uuid(
                session.sid
            )
        except Exception:
            pass
