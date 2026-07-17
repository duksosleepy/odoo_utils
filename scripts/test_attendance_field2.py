# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from odoo.addons.lug_permission.models.hr_employee_access import _lug_filter_web_read_specification

Pub = env["hr.employee.public"].with_user(env["res.users"].browse(58))
spec = {"display_name": {}, "attendance_state": {}, "name": {}}
fs = _lug_filter_web_read_specification(Pub, spec)
print("filtered spec", fs)
try:
    Pub.web_read(spec)
    print("web_read unfiltered OK?")
except Exception as ex:
    print("web_read unfiltered blocked:", type(ex).__name__)
try:
    data = Pub.web_read(fs)
    print("web_read filtered OK", list(data[0].keys()) if data else [])
except Exception as ex:
    print("web_read filtered FAIL", str(ex)[:120])

try:
    data = Pub.web_search_read([], spec, limit=3)
    print("web_search_read OK")
except Exception as ex:
    print("web_search_read FAIL", str(ex)[:150])
