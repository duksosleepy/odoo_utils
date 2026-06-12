{
    "name": "Time Off - Disable Log Note",
    "version": "19.0.1.0.0",
    "category": "Human Resources/Time Off",
    "summary": "Hide the Log note action on Time Off requests",
    "depends": ["hr_holidays", "mail"],
    "assets": {
        "web.assets_backend": [
            "hr_leave_disable_log_note/static/src/xml/chatter.xml",
        ],
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
