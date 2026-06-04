import { threadActionsRegistry } from "@mail/core/common/thread_actions";

const action = threadActionsRegistry.get("open-hr-profile");
if (action) {
    const originalSetup = action.setup;
    action.setup = async function (setupArgs) {
        const thread = setupArgs.thread;
        const partner = thread?.correspondent?.partner_id;
        if (partner && !partner.employeeId) {
            const employees = await this.store.env.services.orm.silent.searchRead(
                "hr.employee.public",
                [["user_partner_id", "=", partner.id]],
                ["id"]
            );
            const employeeId = employees[0]?.id;
            if (employeeId) {
                partner.employeeId = employeeId;
            }
            return;
        }
        if (originalSetup) {
            return originalSetup.call(this, setupArgs);
        }
    };
}
