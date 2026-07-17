# -*- coding: utf-8 -*-
env.cr.execute("SELECT column_name FROM information_schema.columns WHERE table_name='hr_employee' AND column_name='mien'")
print("hr_employee.mien", env.cr.fetchone())
env.cr.execute("SELECT id, mien FROM hr_employee WHERE mien IS NOT NULL LIMIT 5")
print("sample", env.cr.fetchall())
