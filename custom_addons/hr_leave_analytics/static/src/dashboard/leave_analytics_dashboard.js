/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";
import { DateTimeInput } from "@web/core/datetime/datetime_input";

const MIEN_OPTIONS = [
    { value: false, label: "Tất cả miền" },
    { value: "Nam", label: "Miền Nam" },
    { value: "Bắc", label: "Miền Bắc" },
    { value: "ĐTT", label: "Miền ĐTT" },
    { value: "VP", label: "VP" },
];

const WORKFORCE_OPTIONS = [
    { value: false, label: "Tất cả khối" },
    { value: "office", label: "Văn phòng" },
    { value: "store", label: "Cửa hàng" },
];

export class LeaveAnalyticsDashboard extends Component {
    static template = "hr_leave_analytics.LeaveAnalyticsDashboard";
    static components = { DateTimeInput };
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.state = useState({
            loading: true,
            filters: {
                date_from: luxon.DateTime.now().startOf("month"),
                date_to: luxon.DateTime.now(),
                employee_mien: false,
                department_id: false,
                store_id: false,
                workforce_block: false,
                holiday_status_id: false,
            },
            data: null,
        });
        this.mienOptions = MIEN_OPTIONS;
        this.workforceOptions = WORKFORCE_OPTIONS;

        onWillStart(async () => {
            await this.loadDashboard();
        });
    }

    get filtersPayload() {
        const filters = this.state.filters;
        return {
            date_from: filters.date_from ? filters.date_from.toISODate() : false,
            date_to: filters.date_to ? filters.date_to.toISODate() : false,
            employee_mien: filters.employee_mien || false,
            department_id: filters.department_id || false,
            store_id: filters.store_id || false,
            workforce_block: filters.workforce_block || false,
            holiday_status_id: filters.holiday_status_id || false,
        };
    }

    async loadDashboard() {
        this.state.loading = true;
        this.state.data = await this.orm.call(
            "hr.leave.analytics.dashboard",
            "get_dashboard_data",
            [],
            { filters: this.filtersPayload }
        );
        this.state.loading = false;
    }

    async onFilterChange() {
        await this.loadDashboard();
    }

    onDateFromChange(date) {
        this.state.filters.date_from = date;
        this.onFilterChange();
    }

    onDateToChange(date) {
        this.state.filters.date_to = date;
        this.onFilterChange();
    }

    onMienChange(ev) {
        const value = ev.target.value;
        this.state.filters.employee_mien = value || false;
        this.onFilterChange();
    }

    onWorkforceChange(ev) {
        const value = ev.target.value;
        this.state.filters.workforce_block = value || false;
        this.onFilterChange();
    }

    maxChartValue(items) {
        if (!items || !items.length) {
            return 1;
        }
        return Math.max(...items.map((item) => item.value), 1);
    }

    barWidth(value, items) {
        return `${Math.round((value / this.maxChartValue(items)) * 100)}%`;
    }

    pieStyle(items, index) {
        const total = items.reduce((sum, item) => sum + item.value, 0) || 1;
        const colors = ["#4c86f9", "#28a745", "#ffc107", "#dc3545", "#6f42c1", "#17a2b8", "#fd7e14"];
        let start = 0;
        const segments = items.map((item, idx) => {
            const pct = (item.value / total) * 100;
            const segment = `${colors[idx % colors.length]} ${start}% ${start + pct}%`;
            start += pct;
            return segment;
        });
        return {
            background: `conic-gradient(${segments.join(", ")})`,
            opacity: index === null ? 1 : 0.35,
        };
    }

    formatPercent(value) {
        return `${value}%`;
    }

    async drillDown(drillType, recordId = false) {
        const action = await this.orm.call(
            "hr.leave.analytics.dashboard",
            "action_drill_down",
            [],
            {
                drill_type: drillType,
                filters: this.filtersPayload,
                record_id: recordId || false,
            }
        );
        this.actionService.doAction(action);
    }

    async drillDownChart(chartType, item) {
        const mapping = {
            by_type: ["leave_type", item.id],
            by_department: ["department", item.id],
            by_mien: ["mien", item.id],
            by_store: ["store", item.id],
            by_workforce: ["approved_period", false],
        };
        const [drillType, recordId] = mapping[chartType] || ["approved_period", false];
        await this.drillDown(drillType, recordId);
    }
}

registry.category("actions").add("hr_leave_analytics_dashboard", LeaveAnalyticsDashboard);
