# -*- coding: utf-8 -*-
{
    "name": "LUG Task Assignment",
    "version": "19.0.2.0.0",
    "category": "Operations/Task Management",
    "summary": "Giao việc, KPI, SLA, dashboard và phân quyền IT",
    "description": """
LUG Task Assignment — module độc lập, không sửa bảng HR/Time Off.

Giai đoạn 1: Import/Export Excel, master data, KPI tự động + chấm tay.
Giai đoạn 2: Dashboard theo vai trò, Kanban, giao việc UX.
Giai đoạn 3: Workflow phê duyệt, SLA cron, bot Discuss, phân quyền miền/chi nhánh.
    """,
    "depends": [
        "base",
        "mail",
        "hr",
        "hr_store",
        "hr_employee_hrm_detail",
        "hr_job_title_vn",
    ],
    "data": [
        "security/lug_task_security.xml",
        "security/ir.model.access.csv",
        "data/lug_task_sequence.xml",
        "data/lug_task_category_data.xml",
        "data/lug_task_priority_data.xml",
        "data/lug_task_bot_data.xml",
        "data/lug_task_cron.xml",
        "wizard/lug_task_wizard_views.xml",
        "views/lug_task_views.xml",
        "views/lug_task_config_views.xml",
        "views/lug_task_dashboard_views.xml",
        "views/lug_task_menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "lug_task_assignment/static/src/dashboard/lug_task_dashboard.scss",
            "lug_task_assignment/static/src/dashboard/lug_task_dashboard.xml",
            "lug_task_assignment/static/src/dashboard/lug_task_dashboard.js",
        ],
    },
    "post_init_hook": "post_init_hook",
    "license": "LGPL-3",
    "author": "LUG",
    "installable": True,
    "application": True,
    "auto_install": False,
}
