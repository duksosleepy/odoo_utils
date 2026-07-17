# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
env.cr.execute("SELECT id, parent_id, coach_id, user_id FROM hr_employee WHERE id IN (8,71)")
print("employee", env.cr.fetchall())
env.cr.execute("SELECT id, parent_id, coach_id FROM hr_employee_public WHERE id IN (8,71)")
print("public", env.cr.fetchall())
