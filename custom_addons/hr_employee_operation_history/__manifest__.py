{
    'name': 'HR Employee Operation History',
    'version': '19.0.1.0.6',
    'category': 'Human Resources/Employees',
    'summary': 'Ghi lại lịch sử thao tác trên hồ sơ nhân viên',
    'description': """
        HR Employee Operation History
        =============================
        Ghi lại chi tiết các thao tác trên hồ sơ nhân viên:
        - Tạo mới, chỉnh sửa, xóa
        - Người thực hiện và thời gian thao tác
        - Chi tiết thay đổi từng trường (giá trị cũ -> giá trị mới)
    """,
    'depends': ['hr_employee_hrm_detail', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_operation_log_views.xml',
        'views/hr_employee_views.xml',
        'data/backfill_summaries.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'assets': {
        'web.assets_backend': [
            'hr_employee_operation_history/static/src/scss/operation_history.scss',
            'hr_employee_operation_history/static/src/components/operation_history_panel/operation_history_panel.js',
            'hr_employee_operation_history/static/src/components/operation_history_panel/operation_history_panel.xml',
        ],
    },
    'license': 'LGPL-3',
    'author': 'Custom',
    'installable': True,
    'application': False,
    'auto_install': False,
}
