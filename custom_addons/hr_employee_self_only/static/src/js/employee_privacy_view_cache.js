/** @odoo-module **/

import { rpcBus } from "@web/core/network/rpc";
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { viewService } from "@web/views/view_service";

const PRIVACY_MODELS = new Set(["hr.employee", "hr.department"]);

/**
 * Employee/department views bake create/edit flags from has_access() into arch.
 * Skip the disk RPC cache so one reload is enough after permission changes.
 */
patch(viewService, {
    start(env, dependencies) {
        const { loadViews: originalLoadViews } = super.start(env, dependencies);
        const { orm } = dependencies;

        async function loadViews(params, options = {}) {
            const { context, resModel, views } = params;
            if (!PRIVACY_MODELS.has(resModel)) {
                return originalLoadViews(params, options);
            }

            const loadViewsOptions = {
                action_id: options.actionId || false,
                embedded_action_id: options.embeddedActionId || false,
                embedded_parent_res_id: options.embeddedParentResId || false,
                load_filters: options.loadIrFilters || false,
                toolbar: (!context?.disable_toolbar && options.loadActionMenus) || false,
            };
            for (const key in options) {
                if (
                    ![
                        "actionId",
                        "embeddedActionId",
                        "embeddedParentResId",
                        "loadIrFilters",
                        "loadActionMenus",
                    ].includes(key)
                ) {
                    loadViewsOptions[key] = options[key];
                }
            }
            if (env.isSmall) {
                loadViewsOptions.mobile = true;
            }
            if (env.debug) {
                loadViewsOptions.debug = true;
            }
            const filteredContext = Object.fromEntries(
                Object.entries(context || {}).filter(
                    ([k]) => k === "lang" || k.endsWith("_view_ref")
                )
            );

            const result = await orm.call(resModel, "get_views", [], {
                context: filteredContext,
                views,
                options: loadViewsOptions,
            });
            const viewDescriptions = {
                fields: result.models[resModel].fields,
                relatedModels: result.models,
                views: {},
            };
            for (const viewType in result.views) {
                const { arch, toolbar, id, filters, custom_view_id } = result.views[viewType];
                const viewDescription = { arch, id, custom_view_id };
                if (toolbar) {
                    viewDescription.actionMenus = toolbar;
                }
                if (filters) {
                    viewDescription.irFilters = filters;
                }
                viewDescriptions.views[viewType] = viewDescription;
            }
            return viewDescriptions;
        }

        return { loadViews };
    },
});

export const employeePrivacyRefreshService = {
    dependencies: ["bus_service", "action"],
    start(env, { bus_service, action }) {
        bus_service.subscribe("employee_privacy_refresh", () => {
            rpcBus.trigger("CLEAR-CACHES", "get_views");
            action.doAction({ type: "ir.actions.client", tag: "soft_reload" });
        });
    },
};

registry.category("services").add("employee_privacy_refresh", employeePrivacyRefreshService);
