/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";
import {
    LugDonutCard,
    LugHourlyBarCard,
    loadLugChartLib,
} from "./lug_donut_card";

export class LugSecurityDashboard extends Component {
    static template = "lug_security_audit.LugSecurityDashboard";
    static components = { LugDonutCard, LugHourlyBarCard };
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        const today = new Date();
        this.state = useState({
            loading: true,
            data: null,
            filterYear: today.getFullYear(),
            filterMonth: today.getMonth() + 1,
            filterDay: today.getDate(),
            tableSearchText: "",
            tableLoading: false,
            selectedMien: "",
        });
        onWillStart(async () => {
            await loadLugChartLib();
            await this.loadDashboard();
        });
    }

    get dashboardFilters() {
        return {
            year: this.state.filterYear,
            month: this.state.filterMonth,
            day: this.state.filterDay,
            selected_mien: this.state.selectedMien || "",
        };
    }

    get tableFilters() {
        return {
            ...this.dashboardFilters,
            search: this.state.tableSearchText.trim(),
        };
    }

    get exportFilters() {
        return this.tableFilters;
    }

    get filtersPayload() {
        return this.dashboardFilters;
    }

    get donutSections() {
        return this.state.data?.donut_sections || [];
    }

    async loadDashboard() {
        this.state.loading = true;
        try {
            const data = await this.orm.call(
                "lug.security.dashboard",
                "get_dashboard_data",
                [],
                { filters: this.dashboardFilters }
            );
            this.state.data = data;
            if (this.state.tableSearchText.trim()) {
                await this.loadTableRows(false);
            }
        } finally {
            this.state.loading = false;
        }
    }

    async loadTableRows(showLoading = true) {
        if (!this.state.data) {
            await this.loadDashboard();
            return;
        }
        if (showLoading) {
            this.state.tableLoading = true;
        }
        try {
            const rows = await this.orm.call(
                "lug.security.dashboard",
                "get_online_table_rows",
                [],
                { filters: this.tableFilters }
            );
            this.state.data = { ...this.state.data, rows };
        } finally {
            if (showLoading) {
                this.state.tableLoading = false;
            }
        }
    }

    async onFilterChange() {
        await this.loadDashboard();
    }

    async onTableSearchKeydown(ev) {
        if (ev.key === "Enter") {
            await this.loadTableRows();
        }
    }

    async clearTableSearch() {
        this.state.tableSearchText = "";
        await this.loadTableRows();
    }

    async resetFilters() {
        const today = new Date();
        this.state.filterYear = today.getFullYear();
        this.state.filterMonth = today.getMonth() + 1;
        this.state.filterDay = today.getDate();
        this.state.tableSearchText = "";
        this.state.selectedMien = "";
        await this.loadDashboard();
    }

    isDonutClickable(section) {
        return section.key === "tier1" || section.key === "tier2";
    }

    async onMienDonutClick(chart) {
        if ((chart?.key || "").startsWith("store_")) {
            return;
        }
        const mien = chart?.title || "";
        if (!mien || mien === "Tổng quan toàn công ty" || mien === "Tất cả") {
            if (mien === "Tất cả" && this.state.selectedMien) {
                this.state.selectedMien = "";
                await this.loadDashboard();
            }
            return;
        }
        this.state.selectedMien = this.state.selectedMien === mien ? "" : mien;
        await this.loadDashboard();
    }

    getMienClickHandler(chart) {
        return () => this.onMienDonutClick(chart);
    }

    isMienSelected(chart) {
        return this.state.selectedMien && chart.title === this.state.selectedMien;
    }

    async exportExcel() {
        const action = await this.orm.call(
            "lug.security.dashboard",
            "action_export_online",
            [],
            { filters: this.exportFilters }
        );
        this.actionService.doAction(action);
    }
}

registry.category("actions").add("lug_security_dashboard", LugSecurityDashboard);
