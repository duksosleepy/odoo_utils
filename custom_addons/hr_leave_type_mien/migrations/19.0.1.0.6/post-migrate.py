# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    Config = env["hr.leave.mien.config"]
    Line = env["hr.leave.mien.line"]

    if Config.search_count([]):
        return

    cr.execute(
        """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'hr_leave_type_mien'
        )
        """
    )
    if not cr.fetchone()[0]:
        return

    cr.execute("SELECT id, mien, sequence FROM hr_leave_type_mien ORDER BY id")
    for row_id, mien, seq in cr.fetchall():
        config = Config.create({"mien": mien, "sequence": seq or 10})
        cr.execute(
            """
            SELECT leave_type_id
            FROM hr_leave_type_mien_rel
            WHERE config_id = %s
            ORDER BY leave_type_id
            """,
            (row_id,),
        )
        for idx, (leave_type_id,) in enumerate(cr.fetchall()):
            Line.create(
                {
                    "config_id": config.id,
                    "leave_type_id": leave_type_id,
                    "sequence": (idx + 1) * 10,
                }
            )
