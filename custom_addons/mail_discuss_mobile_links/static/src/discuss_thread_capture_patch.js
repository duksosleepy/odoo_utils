/** @odoo-module */

import { Thread } from "@mail/core/common/thread";
import { patch } from "@web/core/utils/patch";
import { hasTouch } from "@web/core/browser/feature_detection";
import { useEffect } from "@odoo/owl";

/**
 * Bắt link ở cấp luồng tin (ô scroll Discuss): trên một số máy `click` không ổn định,
 * thêm `pointerup` / `touchend` capture cùng logic với `handleClickOnLink`.
 */
patch(Thread.prototype, {
    setup() {
        super.setup(...arguments);
        useEffect(
            () => {
                const el = this.root.el;
                if (!el || !this.props.thread) {
                    return;
                }
                let guardUntil = 0;
                const handle = (ev) => {
                    if (typeof ev.isPrimary === "boolean" && !ev.isPrimary) {
                        return;
                    }
                    if (performance.now() < guardUntil) {
                        return;
                    }
                    if (this.store.handleClickOnLink(ev, this.props.thread)) {
                        ev.preventDefault();
                        ev.stopPropagation();
                        guardUntil = performance.now() + 400;
                    }
                };
                el.addEventListener("click", handle, true);
                el.addEventListener("pointerup", handle, true);
                let touchOpts;
                if (hasTouch()) {
                    touchOpts = { capture: true, passive: false };
                    el.addEventListener("touchend", handle, touchOpts);
                }
                return () => {
                    el.removeEventListener("click", handle, true);
                    el.removeEventListener("pointerup", handle, true);
                    if (touchOpts) {
                        el.removeEventListener("touchend", handle, touchOpts);
                    }
                };
            },
            () => [this.props.thread?.id]
        );
    },
});
