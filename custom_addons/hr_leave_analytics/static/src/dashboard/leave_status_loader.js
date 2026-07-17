/** @odoo-module **/

const EMPTY_STATUS_SECTIONS = () => [
    { no: 1, label: "Chờ duyệt", count: 0, items: [] },
    { no: 2, label: "Chờ bàn giao", count: 0, items: [] },
    { no: 3, label: "Từ chối", count: 0, items: [] },
];

const SECTION_KEYS = ["waiting_approval", "waiting_handover", "refused"];

function formatDate(isoDate) {
    if (!isoDate) {
        return "";
    }
    const [year, month, day] = isoDate.split("-");
    return `${day}/${month}/${year}`;
}

function classifyLeave(leave) {
    if (leave.state === "refuse") {
        return "refused";
    }
    const label = (leave.status_display_label || "").toLowerCase();
    if (label.includes("bàn giao")) {
        return "waiting_handover";
    }
    if (leave.handover_status_waiting) {
        return "waiting_handover";
    }
    return "waiting_approval";
}

function buildLeaveLabel(leave) {
    const employeeName = leave.employee_id?.[1] || "";
    const leaveType = leave.holiday_status_id?.[1] || "";
    const dateFrom = formatDate(leave.request_date_from);
    return [employeeName, leaveType, dateFrom].filter(Boolean).join(" — ");
}

function cloneSections() {
    return EMPTY_STATUS_SECTIONS().map((section) => ({
        ...section,
        items: [],
    }));
}

/**
 * Load status counts + employee lines directly from hr.leave (Ngày nghỉ).
 * Same source as menu Tất cả đơn nghỉ phép — no date filter.
 */
export async function loadStatusSectionsFromHrLeave(orm, mienComparison, fixedMien) {
    const domain = [["state", "in", ["confirm", "validate1", "refuse"]]];
    if (fixedMien) {
        domain.push(["employee_leave_mien", "=", fixedMien]);
    }

    const baseFields = [
        "employee_id",
        "holiday_status_id",
        "request_date_from",
        "state",
        "employee_leave_mien",
    ];
    const extraFields = [
        "status_display_label",
        "handover_status_waiting",
        "handover_recipient_display",
    ];

    let leaves = [];
    try {
        leaves = await orm.searchRead(
            "hr.leave",
            domain,
            [...baseFields, ...extraFields],
            { order: "create_date desc, id desc" }
        );
    } catch {
        leaves = await orm.searchRead("hr.leave", domain, baseFields, {
            order: "create_date desc, id desc",
        });
    }

    const rowsByMien = {};
    for (const row of mienComparison) {
        rowsByMien[row.mien] = {
            ...row,
            status_sections: cloneSections(),
        };
    }

    for (const leave of leaves) {
        const mien = leave.employee_leave_mien;
        if (!mien || !rowsByMien[mien]) {
            continue;
        }
        const statusKey = classifyLeave(leave);
        const sectionIdx = SECTION_KEYS.indexOf(statusKey);
        if (sectionIdx < 0) {
            continue;
        }
        let label = buildLeaveLabel(leave);
        if (statusKey === "waiting_handover" && leave.handover_recipient_display) {
            label = `${label} (bàn giao: ${leave.handover_recipient_display})`;
        }
        const section = rowsByMien[mien].status_sections[sectionIdx];
        section.count += 1;
        section.items.push({ label, leave_id: leave.id });
    }

    return mienComparison.map((row) => rowsByMien[row.mien] || row);
}
