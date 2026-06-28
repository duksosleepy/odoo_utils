/** @odoo-module **/

import { loadBundle } from "@web/core/assets";
import { Component, onMounted, onWillUnmount, useEffect, useRef } from "@odoo/owl";

export class LugDonutCard extends Component {
    static template = "lug_security_audit.LugDonutCard";
    static props = {
        chart: { type: Object },
        onSelect: { type: Function, optional: true },
    };

    setup() {
        this.canvasRef = useRef("canvas");
        this.chartInstance = null;

        onMounted(() => this.renderChart());
        onWillUnmount(() => this.destroyChart());
        useEffect(
            () => {
                this.renderChart();
            },
            () => [JSON.stringify(this.props.chart)]
        );
    }

    destroyChart() {
        if (this.chartInstance) {
            this.chartInstance.destroy();
            this.chartInstance = null;
        }
    }

    renderChart() {
        const canvas = this.canvasRef.el;
        const config = this.props.chart;
        if (!canvas || !config || !window.Chart) {
            return;
        }
        this.destroyChart();
        const values = (config.values || []).map((v) => Number(v) || 0);
        const hasData = values.some((v) => v > 0);
        const chartValues = hasData ? values : [1];
        const chartLabels = hasData ? config.labels : ["Không có dữ liệu"];
        const chartColors = hasData ? config.colors : ["#e5e7eb"];

        this.chartInstance = new Chart(canvas, {
            type: "doughnut",
            data: {
                labels: chartLabels,
                datasets: [{
                    data: chartValues,
                    backgroundColor: chartColors,
                    hoverBackgroundColor: chartColors,
                    borderColor: "#ffffff",
                    borderWidth: 3,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "62%",
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            boxWidth: 12,
                            boxHeight: 12,
                            padding: 8,
                            font: { size: 11, weight: "600" },
                            generateLabels: () =>
                                (config.labels || []).map((label, index) => ({
                                    text: `${label}: ${values[index] || 0}`,
                                    fillStyle: (config.colors || [])[index] || "#ccc",
                                    strokeStyle: (config.colors || [])[index] || "#ccc",
                                    fontColor: "#1f2937",
                                    hidden: false,
                                    index,
                                })),
                        },
                        onClick: () => {},
                    },
                    tooltip: {
                        enabled: hasData,
                        callbacks: {
                            label: (ctx) => {
                                const label = chartLabels[ctx.dataIndex];
                                const val = chartValues[ctx.dataIndex];
                                const total = values.reduce((a, b) => a + b, 0) || 1;
                                const pct = Math.round((val / total) * 100);
                                return `${label}: ${val} (${pct}%)`;
                            },
                        },
                    },
                },
                onClick: (_ev, elements) => {
                    if (elements.length && this.props.onSelect) {
                        this.props.onSelect(config);
                    }
                },
            },
            plugins: [{
                id: "lugCenterText",
                beforeDraw: (chart) => {
                    if (!config.center_text) {
                        return;
                    }
                    const { width, height, ctx } = chart;
                    ctx.save();
                    ctx.font = "bold 22px sans-serif";
                    ctx.fillStyle = "#111827";
                    ctx.textAlign = "center";
                    ctx.textBaseline = "middle";
                    ctx.fillText(config.center_text, width / 2, height / 2 - 4);
                    ctx.font = "11px sans-serif";
                    ctx.fillStyle = "#6b7280";
                    ctx.fillText("User", width / 2, height / 2 + 16);
                    ctx.restore();
                },
            }],
        });
    }
}

export class LugHourlyBarCard extends Component {
    static template = "lug_security_audit.LugHourlyBarCard";
    static props = {
        chart: { type: Object },
    };

    setup() {
        this.canvasRef = useRef("canvas");
        this.chartInstance = null;
        onMounted(() => this.renderChart());
        onWillUnmount(() => this.destroyChart());
        useEffect(
            () => this.renderChart(),
            () => [JSON.stringify(this.props.chart)]
        );
    }

    destroyChart() {
        if (this.chartInstance) {
            this.chartInstance.destroy();
            this.chartInstance = null;
        }
    }

    renderChart() {
        const canvas = this.canvasRef.el;
        const config = this.props.chart || {};
        if (!canvas || !window.Chart) {
            return;
        }
        this.destroyChart();
        const labels = config.labels || [];
        const values = (config.values || []).map((v) => Number(v) || 0);
        this.chartInstance = new Chart(canvas, {
            type: "bar",
            data: {
                labels,
                datasets: [{
                    label: "User login",
                    data: values,
                    backgroundColor: "#2563eb",
                    borderRadius: 4,
                }],
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` ${ctx.parsed.x} user`,
                        },
                    },
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: { precision: 0, color: "#374151" },
                        grid: { color: "#e5e7eb" },
                    },
                    y: {
                        ticks: { color: "#111827", font: { weight: "600" } },
                        grid: { display: false },
                    },
                },
            },
        });
    }
}

export async function loadLugChartLib() {
    await loadBundle("web.chartjs_lib");
}
