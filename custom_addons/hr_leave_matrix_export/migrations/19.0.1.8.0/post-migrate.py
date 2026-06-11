# Part of Odoo. See LICENSE file for full copyright and licensing details.


def migrate(cr, version):
    cr.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'hr_leave_file_export_config_backup'
        )
        """
    )
    if not cr.fetchone()[0]:
        return

    cr.execute(
        """
        INSERT INTO hr_leave_file_export_config (
            employee_id,
            sequence,
            employee_hrm_id,
            export_leave_ch,
            export_leave_vp,
            export_import_capnhatcong_ch,
            export_import_capnhatcong_vp,
            create_uid,
            create_date,
            write_uid,
            write_date
        )
        SELECT
            employee_id,
            sequence,
            employee_hrm_id,
            export_leave_ch,
            export_leave_vp,
            export_import_capnhatcong_ch,
            export_import_capnhatcong_vp,
            1,
            NOW() AT TIME ZONE 'UTC',
            1,
            NOW() AT TIME ZONE 'UTC'
        FROM hr_leave_file_export_config_backup
        """
    )
    cr.execute("DROP TABLE hr_leave_file_export_config_backup")
