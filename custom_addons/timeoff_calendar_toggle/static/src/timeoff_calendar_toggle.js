/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { TimeOffCalendarModel } from "@hr_holidays/views/calendar/calendar_model";
import { TimeOffCalendarSidePanel } from "@hr_holidays/views/calendar/calendar_side_panel/calendar_side_panel";

patch(TimeOffCalendarModel.prototype, {
    setup() {
        super.setup(...arguments);
        this.showCalendarEventTime = true;
    },
    setShowCalendarEventTime(show) {
        if (this.showCalendarEventTime === show) {
            return;
        }
        this.showCalendarEventTime = show;
        for (const record of Object.values(this.data.records)) {
            if (record._isTimeHiddenBase !== undefined) {
                record.isTimeHidden = record._isTimeHiddenBase || !this.showCalendarEventTime;
            }
        }
        this.notify();
    },
    normalizeRecord(rawRecord) {
        const result = super.normalizeRecord(...arguments);
        result._isTimeHiddenBase = result.isTimeHidden;
        result.isTimeHidden = result._isTimeHiddenBase || !this.showCalendarEventTime;
        return result;
    },
});

patch(TimeOffCalendarSidePanel.prototype, {
    get showStartTimeLabel() {
        return _t("Show start time");
    },
    onShowStartTimeChange(ev) {
        this.props.model.setShowCalendarEventTime(ev.target.checked);
    },
});
