# -*- coding: utf-8 -*-
{
    "name": "Time Off Calendar — Toggle start time",
    "version": "1.0.0",
    "category": "Human Resources",
    "summary": "Optional checkbox on the Time Off calendar sidebar to show or hide start times on events.",
    "depends": ["hr_holidays"],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "assets": {
        "web.assets_backend": [
            "timeoff_calendar_toggle/static/src/timeoff_calendar_toggle.js",
            "timeoff_calendar_toggle/static/src/timeoff_calendar_toggle.xml",
        ],
    },
}
