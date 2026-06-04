import { patch } from "@web/core/utils/patch";
import { AvatarCardPopover } from "@mail/discuss/web/avatar_card/avatar_card_popover";

/** Staff use hr.employee.public for profile (must load after @hr avatar_card patch). */
patch(AvatarCardPopover.prototype, {
    async getProfileAction() {
        if (!this.employeeId?.id) {
            return super.getProfileAction(...arguments);
        }
        return this.orm.call("hr.employee.public", "get_formview_action", [this.employeeId.id]);
    },
});
