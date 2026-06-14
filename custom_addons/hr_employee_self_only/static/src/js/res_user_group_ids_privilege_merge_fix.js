/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";

/**
 * Keep all privilege selections when one dropdown changes.
 * Core onRecordChanged only receives changed fields, so x2ManyCommands.set()
 * could drop other privileges (e.g. Edit Employee Profile = Allowed).
 */
const reg = registry.category("fields").get("res_user_group_ids");
if (reg?.component) {
    patch(reg.component.prototype, {
        onRecordChanged(record, values) {
            return super.onRecordChanged(record, { ...this.values, ...values });
        },
    });
}
