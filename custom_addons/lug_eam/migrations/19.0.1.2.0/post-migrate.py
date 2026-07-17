# -*- coding: utf-8 -*-


def migrate(cr, version):
    """Bỏ giới hạn độ dài cho cột mã kho (stock_warehouse.code).

    Odoo không tự đổi độ dài varchar khi field bỏ `size`, nên phải ALTER thủ công.
    """
    cr.execute(
        """
        SELECT character_maximum_length
        FROM information_schema.columns
        WHERE table_name = 'stock_warehouse' AND column_name = 'code'
        """
    )
    row = cr.fetchone()
    if row and row[0] is not None:
        cr.execute("ALTER TABLE stock_warehouse ALTER COLUMN code TYPE varchar")
