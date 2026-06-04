/** @odoo-module **/

import { ChatWindow } from "@mail/core/common/chat_window";
import { patch } from "@web/core/utils/patch";

patch(ChatWindow.prototype, {
    onClickHeader(ev) {
        if (
            ev.target.closest(
                ".o-mail-ChatWindow-moreActions, .o-dropdown, .o-mail-ActionList, .o-mail-ChatWindow-counter"
            )
        ) {
            return;
        }
        return super.onClickHeader(...arguments);
    },

    get larkChatWindowDropdownPosition() {
        return this.ui.isSmall ? "bottom-end" : "left-start";
    },

    get larkChatWindowUseBottomSheet() {
        return false;
    },
});
