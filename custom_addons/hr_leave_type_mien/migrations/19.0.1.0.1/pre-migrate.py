# -*- coding: utf-8 -*-

def migrate(cr, version):
    """Lưu dữ liệu cấu hình cũ (1 loại / 1 dòng) trước khi đổi sang Many2many."""
    cr.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'hr_leave_type_mien'
              AND column_name = 'leave_type_id'
        )
        """
    )
    if not cr.fetchone()[0]:
        return
    cr.execute("DROP TABLE IF EXISTS hr_leave_type_mien_legacy")
    cr.execute(
        """
        CREATE TABLE hr_leave_type_mien_legacy AS
        SELECT mien, leave_type_id, sequence
        FROM hr_leave_type_mien
        WHERE mien IS NOT NULL AND leave_type_id IS NOT NULL
        ORDER BY mien, sequence, id
        """
    )
