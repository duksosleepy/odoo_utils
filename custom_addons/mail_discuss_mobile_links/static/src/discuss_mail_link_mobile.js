/** @odoo-module */

import { Store } from "@mail/core/common/store_service";
import { patch } from "@web/core/utils/patch";
import { getOrigin } from "@web/core/utils/urls";

/**
 * @param {MouseEvent} ev
 * @returns {HTMLAnchorElement | null}
 */
function anchorFromDiscussLinkEvent(ev) {
    const direct = ev.target?.closest?.("a");
    if (direct) {
        return direct;
    }
    if (typeof ev.composedPath !== "function") {
        return null;
    }
    for (const node of ev.composedPath()) {
        if (!(node instanceof Element)) {
            continue;
        }
        const nested = node.closest?.("a");
        if (nested) {
            return nested;
        }
    }
    return null;
}

/**
 * @param {HTMLAnchorElement} link
 * @returns {{ model: string, resId: number } | null}
 */
function parseMailViewAccessLink(link) {
    const rawHref = (link?.getAttribute?.("href") || link?.href || "").trim();
    if (!rawHref || rawHref.startsWith("#")) {
        return null;
    }
    const fromQuery = (href) => {
        const m = href.match(/(?:[?#&]|^)(?:amp;)?model=([^&]+)/i);
        const r = href.match(/(?:[?#&]|^)(?:amp;)?res_id=(\d+)/i);
        if (!m || !r) {
            return null;
        }
        const model = decodeURIComponent(m[1].replace(/\+/g, " "));
        const resId = Number(r[1]);
        if (!model || !Number.isFinite(resId) || resId <= 0) {
            return null;
        }
        return { model, resId };
    };
    // Ưu tiên regex trên chuỗi gốc (href tương đối, &amp; trong template, thứ tự query lạ).
    if (/\bmail\/view\b/i.test(rawHref)) {
        const direct = fromQuery(rawHref);
        if (direct) {
            return direct;
        }
    }
    try {
        const url = new URL(rawHref, getOrigin());
        const path = url.pathname || "";
        if (path.includes("/mail/view")) {
            const model = url.searchParams.get("model");
            const resId = Number(url.searchParams.get("res_id"));
            if (model && Number.isFinite(resId) && resId > 0) {
                return { model, resId };
            }
            return fromQuery(url.pathname + url.search) || fromQuery(rawHref);
        }
        const odooRec = path.match(/^\/(?:odoo|scoped_app)\/([^/]+)\/(\d+)\/?$/);
        if (odooRec && !odooRec[1].startsWith("action-")) {
            let model = odooRec[1];
            if (model.startsWith("m-")) {
                model = model.slice(2);
            }
            const resId = Number(odooRec[2]);
            if (model && Number.isFinite(resId) && resId > 0) {
                return { model, resId };
            }
        }
    } catch {
        // Fall through
    }
    return fromQuery(rawHref);
}

patch(Store.prototype, {
    handleClickOnLink(ev, thread) {
        const link = anchorFromDiscussLinkEvent(ev);
        if (!link) {
            return false;
        }
        const mailViewTargets = parseMailViewAccessLink(link);
        if (mailViewTargets) {
            ev.preventDefault();
            const discussLinkOptions = {};
            const inDiscuss =
                Boolean(this.env?.inDiscussApp) ||
                Boolean(this.discuss?.isActive) ||
                thread?.model === "discuss.channel";
            if (this.env.services.ui.isSmall && inDiscuss) {
                discussLinkOptions.stackPosition = "replaceCurrentAction";
            }
            Promise.resolve(
                this.env.services.action.doAction(
                    {
                        type: "ir.actions.act_window",
                        res_model: mailViewTargets.model,
                        views: [[false, "form"]],
                        res_id: mailViewTargets.resId,
                    },
                    discussLinkOptions
                )
            ).then(() => this.onLinkFollowed(thread));
            return true;
        }
        const model = link.dataset.oeModel;
        const id = Number(link.dataset.oeId);
        const handled = super.handleClickOnLink(...arguments);
        if (!handled && model && id) {
            ev.preventDefault();
            const inDiscuss =
                Boolean(this.env?.inDiscussApp) ||
                Boolean(this.discuss?.isActive) ||
                thread?.model === "discuss.channel";
            const doActionOptions =
                this.env.services.ui.isSmall && inDiscuss
                    ? { stackPosition: "replaceCurrentAction" }
                    : {};
            Promise.resolve(
                this.env.services.action.doAction(
                    {
                        type: "ir.actions.act_window",
                        res_model: model,
                        views: [[false, "form"]],
                        res_id: id,
                    },
                    doActionOptions
                )
            ).then(() => this.onLinkFollowed(thread));
            return true;
        }
        return handled;
    },
});
