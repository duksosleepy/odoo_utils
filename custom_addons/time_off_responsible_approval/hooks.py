# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)

_ACTIONABLE_LEAVE_DOMAIN = (
    "[('approval_actionable_user_ids', 'in', [user.id])]"
)
_STANDARD_LEAVE_RULE_XMLIDS = (
    "hr_holidays.hr_leave_rule_responsible_read",
    "hr_holidays.hr_leave_rule_responsible_update",
)


def _repoint_xmlid(env, old_module, old_name, new_module, new_name):
    old = f"{old_module}.{old_name}"
    new = f"{new_module}.{new_name}"
    if old == new:
        return
    imd = env["ir.model.data"].sudo()
    row = imd.search([("module", "=", old_module), ("name", "=", old_name)], limit=1)
    if not row:
        return
    conflict = imd.search([("module", "=", new_module), ("name", "=", new_name)], limit=1)
    if conflict and conflict.res_id != row.res_id:
        return
    row.write({"module": new_module, "name": new_name})


def sync_hr_leave_visibility_rules(env):
    """Override Odoo's noupdate read-all rules with current-approver access."""
    updated = env["ir.rule"]
    for xmlid in _STANDARD_LEAVE_RULE_XMLIDS:
        rule = env.ref(xmlid, raise_if_not_found=False)
        if not rule:
            _logger.warning(
                "time_off_responsible_approval: record rule %s was not found",
                xmlid,
            )
            continue
        if rule.domain_force != _ACTIONABLE_LEAVE_DOMAIN:
            rule.sudo().write({"domain_force": _ACTIONABLE_LEAVE_DOMAIN})
            updated |= rule
    env.registry.clear_cache()
    _logger.info(
        "time_off_responsible_approval: synchronized restricted hr.leave rules %s",
        updated.ids,
    )


def post_init_hook(env):
    _repoint_xmlid(
        env,
        "time_off_extra_approval",
        "ir_cron_escalate_responsible_approval",
        "time_off_responsible_approval",
        "ir_cron_escalate_responsible_approval",
    )
    sync_hr_leave_visibility_rules(env)
