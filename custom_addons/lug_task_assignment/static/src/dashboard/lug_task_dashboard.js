/** @odoo-module **/

import { loadBundle } from "@web/core/assets";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useEffect, useRef, useState } from "@odoo/owl";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

const ROLE_TITLES = {
    board: "Dashboard Tổng Giám Đốc",
    manager: "Dashboard Trưởng phòng",
    team_lead: "Dashboard Tổ trưởng",
    employee: "Dashboard Nhân viên",
};

const KPI_CARDS = [
    { key: "total", label: "Tổng việc", color: "#0d6efd" },
    { key: "completed", label: "Hoàn thành", color: "#198754" },
    { key: "overdue", label: "Quá hạn", color: "#dc3545" },
    { key: "today", label: "Việc hôm nay", color: "#6f42c1" },
    { key: "due_soon", label: "Sắp đến hạn", color: "#fd7e14" },
    { key: "pending_review", label: "Chờ duyệt", color: "#ffc107" },
];

export class LugTaskDashboard extends Component {
    static template = "lug_task_assignment.LugTaskDashboard";
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.statusChartRef = useRef("statusChart");
        this.chart = null;
        const today = new Date();
        this.state = useState({
            loading: true,
            data: null,
            filterOptions: { miens: [], departments: [], stores: [] },
            filterYear: today.getFullYear(),
            filterMonth: today.getMonth() + 1,
            filterMienId: false,
            filterDepartmentId: false,
            filterStoreId: false,
        });
        onWillStart(async () => {
            await loadBundle("web.chartjs_lib");
            await this.loadFilterOptions();
            await this.loadDashboard();
        });
        useEffect(() => {
            if (!this.state.loading && this.state.data) {
                this.renderStatusChart();
            }
            return () => {
                if (this.chart) {
                    this.chart.destroy();
                    this.chart = null;
                }
            };
        });
    }

    get dashboardTitle() {
        const role = this.state.data?.role || "employee";
        return ROLE_TITLES[role] || "Dashboard Giao việc";
    }

    get kpiCards() {
        return KPI_CARDS;
    }

    get filtersPayload() {
        return {
            year: this.state.filterYear,
            month: this.state.filterMonth,
            mien_zone_id: this.state.filterMienId || false,
            department_id: this.state.filterDepartmentId || false,
            store_id: this.state.filterStoreId || false,
        };
    }

    async loadFilterOptions() {
        this.state.filterOptions = await this.orm.call(
            "lug.task.dashboard",
            "get_filter_options",
            []
        );
    }

    async loadDashboard() {
        this.state.loading = true;
        try {
            this.state.data = await this.orm.call(
                "lug.task.dashboard",
                "get_dashboard_data",
                [],
                { filters: this.filtersPayload }
            );
        } finally {
            this.state.loading = false;
        }
    }

    async onFilterChange() {
        await this.loadDashboard();
    }

    async openTasks(domain) {
        await this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Công việc",
            res_model: "lug.task",
            views: [[false, "list"], [false, "kanban"], [false, "form"]],
            domain,
        });
    }

    async openOverdue() {
        await this.openTasks([["is_overdue", "=", true]]);
    }

    async openTask(taskId) {
        if (!taskId) return;
        await this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "lug.task",
            res_id: taskId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    renderStatusChart() {
        const canvas = this.statusChartRef.el;
        if (!canvas || !window.Chart) return;
        const breakdown = this.state.data?.status_breakdown || [];
        if (this.chart) {
            this.chart.destroy();
        }
        this.chart = new window.Chart(canvas, {
            type: "doughnut",
            data: {
                labels: breakdown.map((r) => r.label),
                datasets: [
                    {
                        data: breakdown.map((r) => r.count),
                        backgroundColor: [
                            "#6c757d", "#0d6efd", "#6610f2", "#20c997",
                            "#198754", "#ffc107", "#fd7e14", "#dc3545", "#212529",
                        ],
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: "bottom" } },
            },
        });
    }
}

registry.category("actions").add("lug_task_dashboard", LugTaskDashboard);
