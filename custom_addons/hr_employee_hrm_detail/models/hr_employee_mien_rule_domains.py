# -*- coding: utf-8 -*-
"""domain_force strings for ir.rule (safe_eval, no custom methods)."""

# Officer/staff rules: own profile only (leave_manager_id stays in company comp_rule).
_EMPLOYEE_SELF_FIELDS = ("user_id", "id")
_VERSION_SELF_FIELDS = (
    "employee_id.user_id",
    "employee_id",
    "employee_id.leave_manager_id",
)


def _self_access_tuple(self_fields):
    if self_fields is _VERSION_SELF_FIELDS:
        return _VERSION_SELF_FIELDS
    return _EMPLOYEE_SELF_FIELDS


def _self_access_conditions(self_fields):
    user_field, employee_field, *rest = _self_access_tuple(self_fields)
    manager_field = rest[0] if rest else None
    if manager_field:
        return (
            f"('{user_field}', '=', user.id), "
            f"('{employee_field}', '=', user.employee_id.id), "
            f"('{manager_field}', '=', user.id)"
        )
    return (
        f"('{user_field}', '=', user.id), "
        f"('{employee_field}', '=', user.employee_id.id)"
    )


def _self_domain(self_fields):
    cond = _self_access_conditions(self_fields)
    if self_fields is _VERSION_SELF_FIELDS:
        return f"['|', '|', {cond}]"
    return f"['|', {cond}]"


SELF_DOMAIN = _self_domain(_EMPLOYEE_SELF_FIELDS)
VERSION_SELF_DOMAIN = _self_domain(_VERSION_SELF_FIELDS)


def _resolve_self_fields(self_fields):
    if self_fields is _VERSION_SELF_FIELDS:
        return VERSION_SELF_DOMAIN
    return SELF_DOMAIN


def staff_department_rule_domain(ma_bo_phan_field, self_fields=_EMPLOYEE_SELF_FIELDS):
    self_dom = _resolve_self_fields(self_fields)
    cond = _self_access_conditions(self_fields)
    if self_fields is _VERSION_SELF_FIELDS:
        return (
            f"({self_dom} if not user.employee_ma_bo_phan_id "
            f"else ['|', '|', '|', ('{ma_bo_phan_field}', '=', user.employee_ma_bo_phan_id.id), "
            f"{cond}])"
        )
    return (
        f"({self_dom} if not user.employee_ma_bo_phan_id "
        f"else ['|', '|', ('{ma_bo_phan_field}', '=', user.employee_ma_bo_phan_id.id), "
        f"{cond}])"
    )


def _visibility_or_self_domain(visibility_value, visibility_field, self_fields=_EMPLOYEE_SELF_FIELDS):
    """Flat OR: visibility match OR self-access (never nest SELF_DOMAIN as a sub-list)."""
    cond = _self_access_conditions(self_fields)
    if self_fields is _VERSION_SELF_FIELDS:
        return (
            f"['|', '|', '|', '|', "
            f"('{visibility_field}', '=', '{visibility_value}'), "
            f"('{visibility_field}', '=', 'all'), "
            f"{cond}]"
        )
    return (
        f"['|', '|', '|', "
        f"('{visibility_field}', '=', '{visibility_value}'), "
        f"('{visibility_field}', '=', 'all'), "
        f"{cond}]"
    )


def officer_visibility_rule_domain(visibility_field, self_fields=_EMPLOYEE_SELF_FIELDS):
    self_dom = _resolve_self_fields(self_fields)
    office = _visibility_or_self_domain("office", visibility_field, self_fields)
    store = _visibility_or_self_domain("store", visibility_field, self_fields)
    return (
        f"({office} if user.hr_user_workforce_scope == 'vp' "
        f"else ({store} if user.hr_user_workforce_scope == 'ch' "
        f"else {self_dom}))"
    )


def employee_access_rule_domain(
    visibility_field, ma_bo_phan_field, self_fields=_EMPLOYEE_SELF_FIELDS
):
    staff = staff_department_rule_domain(ma_bo_phan_field, self_fields)
    officer = officer_visibility_rule_domain(visibility_field, self_fields)
    return (
        "[(1, '=', 1)] if user.has_group('hr.group_hr_manager') "
        "else "
        f"({staff}) if user.has_group('hr_employee_hrm_detail.group_hr_employees_staff') "
        "else "
        "[(1, '=', 1)] if user.has_group('hr_employee_hrm_detail.group_hr_employees_supporter') "
        "else "
        f"({officer}) if user.has_group('hr.group_hr_user') "
        "else [(1, '=', 1)]"
    )


HR_EMPLOYEE_MIEN_RULE_DOMAIN = employee_access_rule_domain(
    "employee_visibility", "ma_bo_phan_id"
)
HR_EMPLOYEE_PUBLIC_MIEN_RULE_DOMAIN = employee_access_rule_domain(
    "employee_id.employee_visibility",
    "ma_bo_phan_id",
)
HR_VERSION_MIEN_RULE_DOMAIN = employee_access_rule_domain(
    "employee_id.employee_visibility",
    "employee_id.ma_bo_phan_id",
    self_fields=_VERSION_SELF_FIELDS,
)
