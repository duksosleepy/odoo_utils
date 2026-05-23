from odoo.tools import sql


def migrate(cr, version):
    # Old individual link columns replaced by split_group_id.
    for col in ("p2_leave_id", "p1_leave_id"):
        if sql.column_exists(cr, "hr_leave", col):
            cr.execute(f"ALTER TABLE hr_leave DROP COLUMN {col}")

    if not sql.column_exists(cr, "hr_leave", "split_group_id"):
        cr.execute("ALTER TABLE hr_leave ADD COLUMN split_group_id VARCHAR")
        cr.execute("CREATE INDEX IF NOT EXISTS hr_leave_split_group_id_idx ON hr_leave (split_group_id)")
