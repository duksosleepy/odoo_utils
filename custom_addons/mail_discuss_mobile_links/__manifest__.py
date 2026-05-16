{
    "name": "Discuss — liên kết thông báo trên mobile (Time Off, …)",
    "version": "19.0.1.4.0",
    "category": "Productivity/Discuss",
    "summary": "Mở /mail/view và liên kết data-oe từ Discuss trên màn nhỏ: capture click + thay stack khi cần.",
    "description": "Không sửa code gốc mail: module bổ sung patch JS.",
    "depends": ["mail"],
    "post_init_hook": "post_init_hook",
    "data": [
        "views/mail_notification_layout_inherit.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "mail_discuss_mobile_links/static/src/discuss_mail_link_mobile.js",
            "mail_discuss_mobile_links/static/src/discuss_thread_capture_patch.js",
            "mail_discuss_mobile_links/static/src/discuss_mail_message_capture.js",
            "mail_discuss_mobile_links/static/src/discuss_notification_message_patch.js",
            "mail_discuss_mobile_links/static/src/scss/discuss_mail_link_mobile.scss",
        ],
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
