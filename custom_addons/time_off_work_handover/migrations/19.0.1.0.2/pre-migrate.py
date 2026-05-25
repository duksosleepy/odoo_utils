def migrate(cr, version):
    # Fix stale state on view_hr_leave_form_multi_step left by previous broken
    # upgrade attempts. Previous bad edits may have left arch_db with an xpath
    # targeting 'action_open_refuse_wizard' (which doesn't exist in the base view)
    # and/or a wrong inherit_id. Reset both to a safe neutral state so Odoo can
    # rewrite the record cleanly from the data file during this upgrade.
    cr.execute("""
        UPDATE ir_ui_view
           SET inherit_id = (
               SELECT res_id FROM ir_model_data
                WHERE module = 'hr_holidays' AND name = 'hr_leave_view_form'
           ),
           arch_db = '{"en_US": "<data/>"}'::jsonb,
           arch_updated = FALSE
         WHERE id IN (
               SELECT res_id FROM ir_model_data
                WHERE name = 'view_hr_leave_form_multi_step'
           )
    """)
