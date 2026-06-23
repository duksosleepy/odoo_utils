# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "HR Leave Analytics",
    "version": "19.0.1.0.0",
    "category": "Human Resources/Time Off",
    "summary": "Executive leave dashboard with KPIs, charts, and HR alerts for Sáng Tâm",
    "depends": [
        "hr_holidays",
        "hr_employee_hrm_detail",
        "hr_store",
        "hr_leave_type_mien",
    ],
    "data": [
        "security/hr_leave_analytics_security.xml",
        "security/ir.model.access.csv",
        "views/hr_leave_analytics_report_views.xml",
        "views/hr_leave_analytics_menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "hr_leave_analytics/static/src/dashboard/leave_analytics_dashboard.scss",
            "hr_leave_analytics/static/src/dashboard/leave_analytics_dashboard.xml",
            "hr_leave_analytics/static/src/dashboard/leave_analytics_dashboard.js",
        ],
    },
    "license": "LGPL-3",
    "installable": True,
    "application": False,
}
