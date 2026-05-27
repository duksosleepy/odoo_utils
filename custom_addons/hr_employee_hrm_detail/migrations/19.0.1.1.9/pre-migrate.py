def migrate(cr, version):
    cr.execute("""
        ALTER TABLE hr_employee
            ADD COLUMN IF NOT EXISTS con_lai_nam_truoc DOUBLE PRECISION DEFAULT 0.0,
            ADD COLUMN IF NOT EXISTS nam_chot_con_lai  INTEGER          DEFAULT 0;
    """)
