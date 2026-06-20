# -*- coding: utf-8 -*-
"""Backfill res.users.user_role from current groups / visibility_policy.

Infers a starting role for existing users so the new "Vai trò" selector is not
empty. Does NOT rewrite group membership here (avoids stripping manually granted
access); admins can pick a role explicitly to let the role engine sync groups.

Mapping:
- HR Administrator (hr.group_hr_manager)            -> admin
- HR officer + Time Off officer                     -> hr
- visibility_policy == region                       -> rm
- visibility_policy in (assigned, ma_bo_phan)       -> asm
- otherwise                                          -> employee
"""
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def _infer_role(user):
    if user.has_group("hr.group_hr_manager"):
        return "admin"
    if user.has_group("hr.group_hr_user") and user.has_group(
        "hr_holidays.group_hr_holidays_user"
    ):
        return "hr"
    policy = user.visibility_policy or "self"
    if policy == "region":
        return "rm"
    if policy in ("assigned", "ma_bo_phan"):
        return "asm"
    return "employee"


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    users = env["res.users"].search(
        [("share", "=", False), ("id", "!=", SUPERUSER_ID)]
    )
    count = 0
    for user in users:
        if user.user_role:
            continue
        # Write the field only; skip role-engine group sync on backfill.
        user.with_context(skip_role_apply=True).user_role = _infer_role(user)
        count += 1
    env.registry.clear_cache()
    _logger.info(
        "hr_employee_hrm_detail 19.0.1.1.91: backfilled user_role for %s users",
        count,
    )
