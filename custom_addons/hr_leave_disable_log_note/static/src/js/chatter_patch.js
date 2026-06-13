/** @odoo-module **/

import { Chatter } from "@mail/chatter/web_portal/chatter";
import { onMounted, onPatched } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";

patch(Chatter.prototype, {
    setup() {
        super.setup(...arguments);
        onMounted(() => this._syncTimeOffLogNoteVisibility());
        onPatched(() => this._syncTimeOffLogNoteVisibility());
    },

    _syncTimeOffLogNoteVisibility() {
        const logNoteButton = this.rootRef.el?.querySelector(".o-mail-Chatter-logNote");
        if (logNoteButton) {
            logNoteButton.hidden = this.props.threadModel === "hr.leave";
        }
    },

    toggleComposer(mode = false, options = {}) {
        if (mode === "note" && this.props.threadModel === "hr.leave") {
            return;
        }
        return super.toggleComposer(mode, options);
    },
});
