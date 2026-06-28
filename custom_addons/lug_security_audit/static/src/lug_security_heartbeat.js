/** @odoo-module **/

import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { rpc } from "@web/core/network/rpc";

const lugSecurity = session.lug_security_audit;
if (lugSecurity?.enabled) {
    const intervalMs = lugSecurity.heartbeat_interval_ms || 30000;
    const heartbeat = async () => {
        try {
            await rpc("/lug/security/heartbeat", {});
        } catch {
            // Heartbeat must not disrupt the UI.
        }
    };
    heartbeat();
    setInterval(heartbeat, intervalMs);
    registry.category("services").add("lug_security_heartbeat", {
        start() {},
        dependencies: [],
    });
}
