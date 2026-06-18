# -*- coding: utf-8 -*-
{
    "name": "Refuse Ticket Notifier",
    "version": "19.0.1.0.1",
    "category": "Human Resources",
    "summary": "Notify designated employees when time off requests are refused",
    "description": """
        Add a "Refuse Ticket Notifier" field to Time Off Types.
        When a time off request is refused, the configured employee will receive a notification.
    """,
    "depends": [
        "hr_holidays",
    ],
    "data": [
        "views/hr_leave_type_views.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
}
