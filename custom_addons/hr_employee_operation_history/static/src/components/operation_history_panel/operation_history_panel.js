/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";
import { Component, onWillStart, onWillUpdateProps, useState } from "@odoo/owl";

export class OperationHistoryPanel extends Component {
    static template = "hr_employee_operation_history.OperationHistoryPanel";
    static props = {
        ...standardWidgetProps,
    };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            logs: [],
            loading: false,
        });

        onWillStart(() => this.loadLogs(this.props.record.resId));
        onWillUpdateProps((nextProps) => {
            if (nextProps.record.resId !== this.props.record.resId) {
                return this.loadLogs(nextProps.record.resId);
            }
        });
    }

    async loadLogs(employeeId) {
        if (!employeeId) {
            this.state.logs = [];
            return;
        }
        this.state.loading = true;
        try {
            this.state.logs = await this.orm.call(
                "hr.employee",
                "get_operation_history_panel_data",
                [[employeeId]]
            );
        } finally {
            this.state.loading = false;
        }
    }

    async openLog(logId) {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Operation History"),
            res_model: "hr.employee.operation.log",
            res_id: logId,
            views: [[false, "form"]],
            target: "new",
        });
    }
}

export const operationHistoryPanel = {
    component: OperationHistoryPanel,
};

registry.category("view_widgets").add(
    "hr_employee_operation_history_panel",
    operationHistoryPanel
);
