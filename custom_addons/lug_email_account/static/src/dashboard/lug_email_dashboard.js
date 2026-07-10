/** @odoo-module **/

import { loadBundle } from "@web/core/assets";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useEffect, useRef, useState } from "@odoo/owl";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

const CHART_COLORS = [
    "#ef4444", "#3b82f6", "#22c55e", "#f97316", "#eab308",
    "#a855f7", "#06b6d4", "#ec4899", "#64748b", "#14b8a6",
];

const STATUS_COLORS = {
    "Đang sử dụng": "#22c55e",
    "Tạm khóa": "#f59e0b",
    "Hủy": "#ef4444",
};

const REGION_ORDER = ["Miền Nam", "Miền DTT", "Miền Bắc", "VPHN"];

const REGION_COLORS = {
    "Miền Nam": "#2563eb",
    "Miền DTT": "#14b8a6",
    "Miền Bắc": "#dc2626",
    "VPHN": "#8b5cf6",
    "Chưa phân loại": "#ef4444",
};

const KPI_STATUS_CHARTS = [
    { key: "active", ref: "activeChartRef", chartKey: "active", label: "Đang hoạt động", color: "#22c55e" },
    { key: "cancel", ref: "cancelChartRef", chartKey: "cancel", label: "Đang hủy", color: "#ef4444" },
    { key: "lock", ref: "lockChartRef", chartKey: "lock", label: "Tạm dừng", color: "#f59e0b" },
];

export class LugEmailDashboard extends Component {
    static template = "lug_email_account.LugEmailDashboard";
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.departmentChartRef = useRef("departmentChart");
        this.regionChartRef = useRef("regionChart");
        this.monthChartRef = useRef("monthChart");
        this.activeChartRef = useRef("activeChart");
        this.cancelChartRef = useRef("cancelChart");
        this.lockChartRef = useRef("lockChart");
        this.charts = {
            department: null,
            region: null,
            month: null,
            active: null,
            cancel: null,
            lock: null,
        };
        this.state = useState({
            loading: true,
            data: null,
        });

        onWillStart(async () => {
            await loadBundle("web.chartjs_lib");
            await this.loadDashboard();
        });

        useEffect(
            () => {
                if (!this.state.loading && this.state.data) {
                    requestAnimationFrame(() => this.renderCharts());
                }
                return () => this.destroyCharts();
            },
            () => [this.state.loading, this.state.data]
        );
    }

    destroyCharts() {
        for (const key of Object.keys(this.charts)) {
            if (this.charts[key]) {
                this.charts[key].destroy();
                this.charts[key] = null;
            }
        }
    }

    _colorForDepartment(label, index) {
        if (label === "Chưa phân loại") {
            return "#ef4444";
        }
        return CHART_COLORS[(index + 1) % CHART_COLORS.length];
    }

    _colorForRegion(label) {
        return REGION_COLORS[label] || CHART_COLORS[0];
    }

    _decorateRegionData(data) {
        const total = data.total || 0;
        const summary = data.region_summary || {};
        const serverRows = Array.isArray(data.by_region) ? data.by_region : [];
        const hasServerRegion = serverRows.length > 0 || (summary.legend_rows || []).length > 0;
        const uncategorizedRow = serverRows.find((row) => row.label === "Chưa phân loại");
        const uncategorizedCount = hasServerRegion
            ? (summary.uncategorized_count ?? uncategorizedRow?.count ?? 0)
            : total;
        const classifiedCount = hasServerRegion
            ? (summary.classified_count ?? Math.max(total - uncategorizedCount, 0))
            : 0;
        const classifiedTotal = classifiedCount || 1;

        const sourceRows = hasServerRegion
            ? (
                (summary.legend_rows || []).length
                    ? summary.legend_rows
                    : serverRows.filter((row) => row.label !== "Chưa phân loại")
            )
            : REGION_ORDER.map((label) => ({ label, count: 0 }));

        const legendRows = sourceRows.map((row) => ({
            ...row,
            color: row.color || this._colorForRegion(row.label),
            share_percent:
                row.share_percent ?? Math.round((row.count * 1000) / classifiedTotal) / 10,
        }));

        const decoratedRows = serverRows.length
            ? serverRows.map((row) => ({
                ...row,
                color: row.color || this._colorForRegion(row.label),
            }))
            : legendRows;

        return {
            ...data,
            by_region: decoratedRows,
            region_summary: {
                total: summary.total ?? total,
                classified_count: classifiedCount,
                uncategorized_count: uncategorizedCount,
                legend_rows: legendRows,
            },
        };
    }

    _decorateDepartmentData(data) {
        const rows = data.by_department || [];
        const total = data.total || 0;
        const summary = data.department_summary || {};
        const uncategorized = rows.find((row) => row.label === "Chưa phân loại");
        const classifiedCount = summary.classified_count ?? (total - (uncategorized?.count || 0));
        const classifiedTotal = classifiedCount || 1;

        const colorsByLabel = {};
        rows.forEach((row, index) => {
            colorsByLabel[row.label] = this._colorForDepartment(row.label, index);
        });
        const decoratedRows = rows.map((row) => ({
            ...row,
            color: colorsByLabel[row.label],
        }));
        const legendRows = (summary.legend_rows || decoratedRows.filter(
            (row) => row.label !== "Chưa phân loại"
        )).map((row) => ({
            ...row,
            color: colorsByLabel[row.label],
            share_percent: row.share_percent ?? Math.round((row.count * 1000) / classifiedTotal) / 10,
        }));

        return {
            ...data,
            by_department: decoratedRows,
            department_summary: {
                total: summary.total ?? total,
                classified_count: classifiedCount,
                uncategorized_count: summary.uncategorized_count ?? (uncategorized?.count || 0),
                legend_rows: legendRows,
            },
        };
    }

    get regionSummary() {
        const summary = this.state.data?.region_summary;
        const total = this.state.data?.total || 0;
        return {
            total: summary?.total ?? total,
            classified_count: summary?.classified_count ?? 0,
            uncategorized_count: summary?.uncategorized_count ?? 0,
            legend_rows: summary?.legend_rows || [],
        };
    }

    get departmentSummary() {
        const summary = this.state.data?.department_summary;
        const total = this.state.data?.total || 0;
        return {
            total: summary?.total ?? total,
            classified_count: summary?.classified_count ?? 0,
            uncategorized_count: summary?.uncategorized_count ?? 0,
            legend_rows: summary?.legend_rows || [],
        };
    }

    async loadDashboard() {
        this.state.loading = true;
        try {
            const data = await this.orm.call(
                "lug.email.dashboard",
                "get_dashboard_data",
                []
            );
            this.state.data = this._decorateRegionData(
                this._decorateDepartmentData(data)
            );
        } finally {
            this.state.loading = false;
        }
    }

    _colorsForLabels(labels, palette = CHART_COLORS) {
        return labels.map((label, index) => STATUS_COLORS[label] || palette[index % palette.length]);
    }

    _legendLabel(row) {
        return `${row.label} (${row.count} - ${row.percent || 0}%)`;
    }

    renderDoughnutChart(refName, chartKey, rows, title, { withCounts = false, showLegend = true } = {}) {
        const canvas = this[refName].el;
        if (!canvas || !window.Chart) {
            return;
        }
        if (this.charts[chartKey]) {
            this.charts[chartKey].destroy();
        }
        const labels = withCounts
            ? rows.map((row) => this._legendLabel(row))
            : rows.map((row) => row.label);
        const data = rows.map((row) => row.count);
        const backgroundColor = rows.map(
            (row, index) => row.color || this._colorForDepartment(row.label, index)
        );
        this.charts[chartKey] = new window.Chart(canvas, {
            type: "doughnut",
            data: {
                labels,
                datasets: [
                    {
                        label: title,
                        data,
                        backgroundColor,
                        borderWidth: 1,
                        borderColor: "#fff",
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "62%",
                plugins: {
                    legend: {
                        display: showLegend,
                        position: "bottom",
                        labels: { boxWidth: 12, padding: 12, font: { size: 11 } },
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const row = rows[context.dataIndex];
                                return `${row.label}: ${row.count} (${row.percent || 0}%)`;
                            },
                        },
                    },
                },
            },
        });
    }

    renderStatusKpiChart(card) {
        const canvas = this[card.ref].el;
        if (!canvas || !window.Chart) {
            return;
        }
        if (this.charts[card.chartKey]) {
            this.charts[card.chartKey].destroy();
        }
        const total = this.state.data?.kpi?.total || 0;
        const value = this.state.data?.kpi?.[card.key] || 0;
        const rest = Math.max(total - value, 0);
        this.charts[card.chartKey] = new window.Chart(canvas, {
            type: "doughnut",
            data: {
                labels: [card.label, "Khác"],
                datasets: [
                    {
                        data: [value, rest],
                        backgroundColor: [card.color, "#e5e7eb"],
                        borderWidth: 0,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "72%",
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                if (context.dataIndex !== 0) {
                                    return null;
                                }
                                return `${card.label}: ${value}`;
                            },
                        },
                    },
                },
            },
        });
    }

    renderRegionChart() {
        const canvas = this.regionChartRef.el;
        if (!canvas || !window.Chart) {
            return;
        }
        if (this.charts.region) {
            this.charts.region.destroy();
        }
        const rows = (this.regionSummary.legend_rows || []).filter(
            (row) => row.label !== "Chưa phân loại"
        );
        const chartRows = rows.length
            ? rows
            : REGION_ORDER.map((label) => ({
                label,
                count: 0,
                color: this._colorForRegion(label),
            }));
        this.charts.region = new window.Chart(canvas, {
            type: "bar",
            data: {
                labels: chartRows.map((row) => row.label),
                datasets: [
                    {
                        label: "Số email",
                        data: chartRows.map((row) => row.count),
                        backgroundColor: chartRows.map(
                            (row) => row.color || this._colorForRegion(row.label)
                        ),
                        borderRadius: 8,
                        maxBarThickness: 48,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const row = chartRows[context.dataIndex];
                                return `${row.label}: ${row.count}`;
                            },
                        },
                    },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { precision: 0 },
                    },
                    x: {
                        ticks: {
                            font: { size: 11 },
                            maxRotation: 0,
                            minRotation: 0,
                        },
                    },
                },
            },
        });
    }

    renderMonthChart() {
        const canvas = this.monthChartRef.el;
        if (!canvas || !window.Chart) {
            return;
        }
        if (this.charts.month) {
            this.charts.month.destroy();
        }
        const series = this.state.data?.by_month || { labels: [], counts: [] };
        this.charts.month = new window.Chart(canvas, {
            type: "bar",
            data: {
                labels: series.labels,
                datasets: [
                    {
                        label: "Số email tạo mới",
                        data: series.counts,
                        backgroundColor: "#714b67",
                        borderRadius: 6,
                        maxBarThickness: 42,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { precision: 0 },
                    },
                },
            },
        });
    }

    renderCharts() {
        const data = this.state.data || {};
        this.renderDoughnutChart(
            "departmentChartRef",
            "department",
            data.by_department || [],
            "Email theo phòng ban",
            { showLegend: false }
        );
        this.renderRegionChart();
        for (const card of KPI_STATUS_CHARTS) {
            this.renderStatusKpiChart(card);
        }
        this.renderMonthChart();
    }

    async openEmail(recordId) {
        if (!recordId) {
            return;
        }
        await this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "lug.email.account",
            res_id: recordId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    async openAllEmails() {
        await this.actionService.doAction("lug_email_account.action_lug_email_list_all");
    }
}

registry.category("actions").add("lug_email_dashboard", LugEmailDashboard);
