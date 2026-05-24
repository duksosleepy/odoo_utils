# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    cr.execute(
        """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'hr_leave_type_mien_legacy'
        )
        """
    )
    if not cr.fetchone()[0]:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    MienConfig = env["hr.leave.type.mien"]

    cr.execute("SELECT DISTINCT mien FROM hr_leave_type_mien_legacy ORDER BY mien")
    for (mien,) in cr.fetchall():
        cr.execute(
            """
            SELECT leave_type_id
            FROM hr_leave_type_mien_legacy
            WHERE mien = %s
            ORDER BY sequence, leave_type_id
            """,
            (mien,),
        )
        type_ids = [row[0] for row in cr.fetchall() if row[0]]
        configs = MienConfig.search([("mien", "=", mien)])
        config = configs[:1]
        if len(configs) > 1:
            configs[1:].unlink()
        if not config:
            config = MienConfig.create({"mien": mien})
        config.leave_type_ids = [(6, 0, type_ids)]

    cr.execute("DROP TABLE hr_leave_type_mien_legacy")
