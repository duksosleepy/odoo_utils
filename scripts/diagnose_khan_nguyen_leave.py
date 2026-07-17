# -*- coding: utf-8 -*-
import sys
from datetime import timedelta

from odoo import fields

sys.stdout.reconfigure(encoding="utf-8")

login = "khan.nguyen@sangtam.com"
user = env["res.users"].sudo().search([("login", "=", login)], limit=1)
if not user:
    print("USER NOT FOUND:", login)
    raise SystemExit(1)

print("=== USER ===")
print("id:", user.id, "name:", user.name, "active:", user.active)
emp = user.employee_id
print("employee_id:", emp.id if emp else None, emp.name if emp else None)
if emp:
    print("job_title:", getattr(emp, "job_title", None))
    print("leave_manager_id:", emp.leave_manager_id.id if emp.leave_manager_id else None, emp.leave_manager_id.name if emp.leave_manager_id else None)
    print("department:", emp.department_id.name if emp.department_id else None)
    if hasattr(emp, "employee_mien"):
        print("employee_mien:", emp.employee_mien)
    if hasattr(emp, "mien_id"):
        print("mien_id:", emp.mien_id.name if emp.mien_id else None)

groups = user.all_group_ids.mapped("full_name")
print("groups (hr/timeoff related):")
for g in sorted(groups):
    if any(x in g.lower() for x in ("holiday", "leave", "hr", "lug", "time")):
        print(" ", g)

uenv = env["hr.leave"].with_user(user)
print("\n=== LEAVE TYPES (accessible) ===")
LeaveType = env["hr.leave.type"].with_user(user)
types = LeaveType.search([])
for lt in types[:15]:
    print(
        f"  {lt.id} {lt.name!r} validation={lt.leave_validation_type} "
        f"requires_allocation={lt.requires_allocation}"
    )
print("  total types:", len(types))

print("\n=== RECENT LEAVES ===")
leaves = uenv.search([("employee_id", "=", emp.id)], order="id desc", limit=5)
for lv in leaves:
    print(
        f"  leave {lv.id} state={lv.state} type={lv.holiday_status_id.name!r} "
        f"validation={lv.validation_type} from={lv.request_date_from} to={lv.request_date_to}"
    )

print("\n=== SIMULATE _check_approval_update on confirm ===")
if leaves:
    lv = leaves[0]
    try:
        lv.with_user(user)._check_approval_update("confirm", raise_if_not_possible=True)
        print("  confirm: OK")
    except Exception as ex:
        print("  confirm: FAIL", ex)

print("\n=== SIMULATE _check_approval_update on validate ===")
if leaves:
    lv = leaves[0]
    try:
        lv.with_user(user)._check_approval_update("validate", raise_if_not_possible=True)
        print("  validate: OK")
    except Exception as ex:
        print("  validate: FAIL", ex)

print("\n=== SIMULATE create draft leave (dry) ===")
if types and emp:
    lt = types[0]
    today = fields.Date.context_today(uenv)
    start = today + timedelta(days=10)
    vals = {
        "name": "TEST diagnose",
        "employee_id": emp.id,
        "holiday_status_id": lt.id,
        "request_date_from": start,
        "request_date_to": start,
        "date_from": fields.Datetime.to_datetime(start),
        "date_to": fields.Datetime.to_datetime(start),
    }
    print("  using type:", lt.name, "validation:", lt.leave_validation_type)
    try:
        preview = uenv.check_leave_form_save_confirmations(res_id=False, vals=vals)
        print("  save preview:", preview)
    except Exception as ex:
        print("  save preview FAIL:", ex)

    is_officer = user.has_group("hr_holidays.group_hr_holidays_user")
    is_manager = user.has_group("hr_holidays.group_hr_holidays_manager")
    print("  is_officer:", is_officer, "is_manager:", is_manager)
    print("  user == leave_manager:", user == emp.leave_manager_id)
    print("  user == employee.user:", user == emp.user_id)

print("\n=== SIMULATE create + confirm (rollback) ===")
if types and emp:
    lt = None
    for candidate in types:
        try:
            with env.cr.savepoint():
                env["hr.leave"].with_user(user).create({
                    "name": "probe",
                    "employee_id": emp.id,
                    "holiday_status_id": candidate.id,
                    "request_date_from": fields.Date.today() + timedelta(days=30),
                    "request_date_to": fields.Date.today() + timedelta(days=30),
                })
            lt = candidate
            break
        except Exception:
            continue
    if not lt:
        lt = types[0]
        print("  WARNING: no leave type passed probe create; using first type")
    today = fields.Date.context_today(uenv)
    start = today + timedelta(days=10)
    end = start + timedelta(days=1)
    ctx = dict(env.context, **{
        "default_employee_id": emp.id,
        "skip_handover_submit_bot_notify": True,
        "skip_responsible_submit_notify": True,
    })
    try:
        with env.cr.savepoint():
            leave = env["hr.leave"].with_user(user).with_context(**ctx).create({
                "name": "DIAG test leave",
                "employee_id": emp.id,
                "holiday_status_id": lt.id,
                "request_date_from": start,
                "request_date_to": end,
                "date_from": fields.Datetime.to_datetime(start),
                "date_to": fields.Datetime.to_datetime(end + timedelta(days=1)),
            })
            print(f"  created leave {leave.id} state={leave.state} validation={leave.validation_type}")
            for st in ("confirm", "validate1", "validate"):
                try:
                    leave.with_user(user)._check_approval_update(st, raise_if_not_possible=True)
                    print(f"  _check_approval_update({st!r}): OK")
                except Exception as ex:
                    print(f"  _check_approval_update({st!r}): FAIL -> {ex}")
            try:
                leave.with_user(user).action_confirm()
                print(f"  action_confirm: OK state={leave.state}")
            except Exception as ex:
                print(f"  action_confirm: FAIL -> {ex}")
    except Exception as ex:
        print("  create FAIL:", ex)
