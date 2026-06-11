# Part of Odoo. See LICENSE file for full copyright and licensing details.


def migrate(cr, version):
    cr.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'hr_leave_file_export_config'
              AND column_name = 'export_file_type'
        )
        """
    )
    if not cr.fetchone()[0]:
        return

    cr.execute(
        """
        CREATE TABLE IF NOT EXISTS hr_leave_file_export_config_backup (
            employee_id INTEGER NOT NULL PRIMARY KEY,
            sequence INTEGER,
            employee_hrm_id VARCHAR,
            export_leave_ch BOOLEAN DEFAULT FALSE,
            export_leave_vp BOOLEAN DEFAULT FALSE,
            export_import_capnhatcong_ch BOOLEAN DEFAULT FALSE,
            export_import_capnhatcong_vp BOOLEAN DEFAULT FALSE
        )
        """
    )
    cr.execute("DELETE FROM hr_leave_file_export_config_backup")
    cr.execute(
        """
        INSERT INTO hr_leave_file_export_config_backup (
            employee_id,
            sequence,
            employee_hrm_id,
            export_leave_ch,
            export_leave_vp,
            export_import_capnhatcong_ch,
            export_import_capnhatcong_vp
        )
        SELECT
            employee_id,
            MIN(sequence),
            MIN(employee_hrm_id),
            BOOL_OR(export_file_type = 'leave_ch'),
            BOOL_OR(export_file_type = 'leave_vp'),
            BOOL_OR(export_file_type = 'import_capnhatcong'),
            BOOL_OR(export_file_type = 'import_capnhatcong_vp')
        FROM hr_leave_file_export_config
        GROUP BY employee_id
        """
    )
    cr.execute("DELETE FROM hr_leave_file_export_config")
