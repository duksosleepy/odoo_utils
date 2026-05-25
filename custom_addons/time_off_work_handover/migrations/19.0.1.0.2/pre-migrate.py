def migrate(cr, version):
    # Reset the inherit_id of view_hr_leave_form_multi_step to point at
    # hr_holidays.hr_leave_view_form. A previous broken upgrade may have left it
    # pointing at a wrong parent, which causes view-validation to fail when the
    # arch (which uses xpath against the base form) is re-written during upgrade.
    cr.execute("""
        UPDATE ir_ui_view v
           SET inherit_id = base.id
          FROM ir_ui_view base
          JOIN ir_model_data imd_base
            ON imd_base.res_id = base.id
           AND imd_base.module = 'hr_holidays'
           AND imd_base.name   = 'hr_leave_view_form'
          JOIN ir_model_data imd_v
            ON imd_v.res_id = v.id
           AND imd_v.name   = 'view_hr_leave_form_multi_step'
         WHERE v.inherit_id IS DISTINCT FROM base.id
    """)
