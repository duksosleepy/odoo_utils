# Drop leftover export_kind column/field metadata (removed in 19.0.1.2.1).


def migrate(cr, version):
    cr.execute(
        """
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'hr_leave_matrix_export_wizard' AND column_name = 'export_kind'
        """
    )
    if cr.fetchone():
        cr.execute('ALTER TABLE "hr_leave_matrix_export_wizard" DROP COLUMN "export_kind"')

    cr.execute(
        """
        DELETE FROM ir_model_fields
        WHERE model = 'hr.leave.matrix.export.wizard' AND name = 'export_kind'
        """
    )
