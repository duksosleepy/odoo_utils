/** @odoo-module **/

import { registry } from "@web/core/registry";
import { session } from "@web/session";

const systray = registry.category("systray");

if (session.lug_ui?.hide_messaging) {
    systray.remove("mail.messaging_menu");
}
if (session.lug_ui?.hide_activities) {
    systray.remove("mail.activity_menu");
}
