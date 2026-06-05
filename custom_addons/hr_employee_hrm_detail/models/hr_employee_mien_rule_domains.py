# -*- coding: utf-8 -*-
"""domain_force strings for ir.rule (safe_eval, no custom methods)."""

MIEN_BND = ("Bắc", "Nam", "ĐTT")

_EMPLOYEE_SELF_FIELDS = ("user_id", "id", "leave_manager_id")
_VERSION_SELF_FIELDS = (
    "employee_id.user_id",
    "employee_id",
    "employee_id.leave_manager_id",
)


def _self_access_conditions(user_field, employee_field, manager_field):
    return (
        f"('{user_field}', '=', user.id), "
        f"('{employee_field}', '=', user.employee_id.id), "
        f"('{manager_field}', '=', user.id)"
    )


def _self_domain(user_field, employee_field, manager_field):
    cond = _self_access_conditions(user_field, employee_field, manager_field)
    return f"['|', '|', {cond}]"


_SELF_ACCESS_CONDITIONS = _self_access_conditions(*_EMPLOYEE_SELF_FIELDS)
SELF_DOMAIN = _self_domain(*_EMPLOYEE_SELF_FIELDS)
_VERSION_SELF_ACCESS_CONDITIONS = _self_access_conditions(*_VERSION_SELF_FIELDS)
VERSION_SELF_DOMAIN = _self_domain(*_VERSION_SELF_FIELDS)


def _resolve_self_fields(self_fields):
    if self_fields is _VERSION_SELF_FIELDS:
        return _VERSION_SELF_FIELDS, VERSION_SELF_DOMAIN
    return _EMPLOYEE_SELF_FIELDS, SELF_DOMAIN


def staff_department_rule_domain(ma_bo_phan_field, self_fields=_EMPLOYEE_SELF_FIELDS):
    user_field, employee_field, manager_field = _resolve_self_fields(self_fields)[0]
    self_dom = _resolve_self_fields(self_fields)[1]
    cond = _self_access_conditions(user_field, employee_field, manager_field)
    return (
        f"({self_dom} if not user.employee_ma_bo_phan_id "
        f"else ['|', '|', '|', ('{ma_bo_phan_field}', '=', user.employee_ma_bo_phan_id.id), "
        f"{cond}])"
    )


def _mien_or_self_domain(mien_field, dept_field, mien_values_repr, self_fields=_EMPLOYEE_SELF_FIELDS):
    """Flat OR: Miền match OR self-access (never nest SELF_DOMAIN as a sub-list)."""
    user_field, employee_field, manager_field = _resolve_self_fields(self_fields)[0]
    cond = _self_access_conditions(user_field, employee_field, manager_field)
    return (
        f"['|', '|', '|', '|', "
        f"('{mien_field}', 'in', {mien_values_repr}), "
        f"'&', ('{mien_field}', '=', False), ('{dept_field}', 'in', {mien_values_repr}), "
        f"{cond}]"
    )


def officer_mien_rule_domain(mien_field, dept_field, self_fields=_EMPLOYEE_SELF_FIELDS):
    self_dom = _resolve_self_fields(self_fields)[1]
    vp = _mien_or_self_domain(mien_field, dept_field, "['VP']", self_fields)
    bnd = _mien_or_self_domain(mien_field, dept_field, repr(list(MIEN_BND)), self_fields)
    return (
        f"({vp} if user.hr_officer_mien_scope == 'vp' "
        f"else ({bnd} if user.hr_officer_mien_scope == 'bnd' "
        f"else {self_dom}))"
    )


def employee_access_rule_domain(
    mien_field, dept_mien_field, ma_bo_phan_field, self_fields=_EMPLOYEE_SELF_FIELDS
):
    staff = staff_department_rule_domain(ma_bo_phan_field, self_fields)
    officer = officer_mien_rule_domain(mien_field, dept_mien_field, self_fields)
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
    "mien", "ma_bo_phan_id.mien", "ma_bo_phan_id"
)
HR_EMPLOYEE_PUBLIC_MIEN_RULE_DOMAIN = employee_access_rule_domain(
    "employee_id.mien",
    "employee_id.ma_bo_phan_id.mien",
    "ma_bo_phan_id",
)
HR_VERSION_MIEN_RULE_DOMAIN = employee_access_rule_domain(
    "employee_id.mien",
    "employee_id.ma_bo_phan_id.mien",
    "employee_id.ma_bo_phan_id",
    self_fields=_VERSION_SELF_FIELDS,
)
