/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ExportAll } from "@web/views/list/export_all/export_all";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { xml } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

// ExportAll is only mounted when the standard "Export All" cog rules already pass
// (list/kanban, export group, export_xlsx, no selection). Restrict to Time Off model only.
patch(ExportAll, {
    components: { DropdownItem },
    template: xml`
        <DropdownItem class="'o_export_all_menu'" onSelected.bind="onDirectExportData">
            <i class="fa fa-fw fa-upload me-1"/>Export All
        </DropdownItem>
        <DropdownItem
            t-if="env.model and env.model.root and env.model.root.resModel === 'hr.leave'"
            class="'o_hr_leave_matrix_export_menu'"
            onSelected.bind="onMatrixExport">
            <i class="fa fa-fw fa-table me-1"/>Export Excel file (matrix)
        </DropdownItem>
    `,
});

patch(ExportAll.prototype, {
    async onMatrixExport() {
        const sm = this.env.searchModel;
        const domain = sm ? sm.domain : [];
        const today = luxon.DateTime.local();
        await this.env.services.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Export time off matrix (Excel)"),
            res_model: "hr.leave.matrix.export.wizard",
            views: [[false, "form"]],
            target: "new",
            context: {
                default_year: today.year,
                default_month: today.month,
                matrix_export_domain_json: JSON.stringify(domain),
            },
        });
    },
});
