/** @odoo-module */

import { NotificationMessage } from "@mail/core/common/notification_message";
import { patch } from "@web/core/utils/patch";
import { useEffect } from "@odoo/owl";

/**
 * Thông báo dạng `notification` trong Discuss dùng `NotificationMessage`, không đi qua
 * `Message` → patch capture ở đây để nút "Time Off" / mail/view vẫn bắt được tap (mobile).
 */
patch(NotificationMessage.prototype, {
    setup() {
        super.setup(...arguments);
        useEffect(
            () => {
                const el = this.root.el;
                if (!el) {
                    return;
                }
                const onCaptureClick = (ev) => {
                    if (this.store.handleClickOnLink(ev, this.props.thread)) {
                        ev.preventDefault();
                        ev.stopPropagation();
                    }
                };
                el.addEventListener("click", onCaptureClick, true);
                return () => el.removeEventListener("click", onCaptureClick, true);
            },
            () => [this.message.richBody, this.message.id]
        );
    },
    async onClickNotificationMessage(ev) {
        if (this.store.handleClickOnLink(ev, this.props.thread)) {
            ev.preventDefault();
            ev.stopPropagation();
            return;
        }
        await super.onClickNotificationMessage(...arguments);
    },
});
