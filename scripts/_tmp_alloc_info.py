# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
for tid in [75, 76, 78, 81, 82, 83, 84]:
    t = env["hr.leave.type"].sudo().browse(tid)
    if t.exists():
        print(f"{tid} {t.name} requires_alloc={t.requires_allocation} validation={t.leave_validation_type}")
