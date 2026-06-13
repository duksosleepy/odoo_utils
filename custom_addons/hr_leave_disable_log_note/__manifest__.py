{
    "name": "Time Off - Disable Log Note",
    "version": "19.0.1.1.0",
    "category": "Human Resources/Time Off",
    "summary": "Hide the Log note action on Time Off requests",
    "depends": ["hr_holidays", "mail"],
    "assets": {
        "web.assets_backend": [
            "hr_leave_disable_log_note/static/src/js/chatter_patch.js",
        ],
    },
    "installable": True,
    "application": False,
    "author": "Custom",
    "license": "LGPL-3",
}
