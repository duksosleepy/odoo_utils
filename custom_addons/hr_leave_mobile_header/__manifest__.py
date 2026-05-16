{
    "name": "Time Off Form — Mobile header like desktop",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "summary": "On small screens, hide the leave statusbar and show all header "
    "actions in one row (no three-dots menu) for hr.leave forms.",
    "depends": ["hr_holidays", "web"],
    "data": [
        "views/hr_leave_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "hr_leave_mobile_header/static/src/xml/status_bar_buttons_hr_leave.xml",
        ],
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
