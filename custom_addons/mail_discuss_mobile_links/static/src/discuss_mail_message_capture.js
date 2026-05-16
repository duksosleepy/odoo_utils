/** @odoo-module */

import { Message } from "@mail/core/common/message";
import { patch } from "@web/core/utils/patch";
import { useEffect } from "@odoo/owl";

patch(Message.prototype, {
    setup() {
        super.setup(...arguments);
        useEffect(
            () => {
                const el = this.root.el;
                if (!el || !this.message.exists() || this.isEditing) {
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
            () => [
                this.isEditing,
                this.message.richBody,
                this.message.id,
                this.message.showTranslation,
            ]
        );
    },
});
