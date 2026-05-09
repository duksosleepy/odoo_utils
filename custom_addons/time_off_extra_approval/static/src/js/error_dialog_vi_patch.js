/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { odooExceptionTitleMap } from "@web/core/errors/error_dialogs";

// Keep default validation popup title translatable per active language.
odooExceptionTitleMap.set("odoo.exceptions.ValidationError", _t("Validation Error"));
