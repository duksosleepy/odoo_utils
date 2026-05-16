/** @odoo-module **/

import { Message } from "@mail/core/common/message";
import { Store } from "@mail/core/common/store_service";
import { browser } from "@web/core/browser/browser";
import { patch } from "@web/core/utils/patch";
import { onMounted, onWillDestroy } from "@odoo/owl";

const LEAVE_LINK_SELECTOR = [
    'a[data-oe-model="hr.leave"][data-oe-id]',
    'a[data-oe-type="handover"][data-oe-id]',
    'a[data-oe-type="approval"][data-oe-id]',
    'a[href*="/hr.leave/"]',
    'a[href*="/discuss_leave/"]',
].join(", ");

function findTimeOffLeaveLink(target) {
    return target?.closest?.(LEAVE_LINK_SELECTOR) ?? null;
}

function resolveLeaveId(link) {
    if (!link) {
        return 0;
    }
    const fromData = Number(link.dataset.oeId);
    if (fromData) {
        return fromData;
    }
    const href = link.getAttribute("href") || link.pathname || "";
    const m = href.match(/(?:hr\.leave\/|discuss_leave\/)(\d+)/);
    return m ? Number(m[1]) : 0;
}

function foldMobileChatWindow(store, ev, thread, link) {
    if (
        !store.env.services.ui.isSmall ||
        !ev.target.closest(".o-mail-ChatWindow") ||
        !link.href
    ) {
        return;
    }
    try {
        const url = new URL(link.href);
        if (
            browser.location.host === url.host &&
            browser.location.pathname.startsWith("/odoo")
        ) {
            store.ChatWindow.get({ thread })?.fold();
        }
    } catch {
        // ignore invalid URLs
    }
}

function openLeaveForm(env, resId) {
    return env.services.action.doAction({
        type: "ir.actions.act_window",
        res_model: "hr.leave",
        res_id: resId,
        views: [[false, "form"]],
        target: "current",
    });
}

function handleTimeOffLeaveLink(ev, store, thread) {
    const link = findTimeOffLeaveLink(ev.target);
    if (!link) {
        return false;
    }
    const resId = resolveLeaveId(link);
    if (!resId) {
        return false;
    }
    ev.preventDefault();
    ev.stopPropagation();
    foldMobileChatWindow(store, ev, thread, link);
    openLeaveForm(store.env, resId);
    return true;
}

patch(Store.prototype, {
    handleClickOnLink(ev, thread) {
        if (handleTimeOffLeaveLink(ev, this, thread)) {
            return true;
        }
        return super.handleClickOnLink(...arguments);
    },
});

patch(Message.prototype, {
    setup() {
        super.setup(...arguments);
        const onTimeOffLinkTap = (ev) => {
            if (!this.root.el?.contains(ev.target)) {
                return;
            }
            handleTimeOffLeaveLink(ev, this.store, this.props.thread);
        };
        onMounted(() => {
            this.root.el?.addEventListener("click", onTimeOffLinkTap, { capture: true });
        });
        onWillDestroy(() => {
            this.root.el?.removeEventListener("click", onTimeOffLinkTap, { capture: true });
        });
    },
});
