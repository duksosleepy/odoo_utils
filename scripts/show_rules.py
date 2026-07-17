# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

env.cr.execute("""
SELECT r.id, r.domain_force, r.active
FROM ir_rule r
JOIN ir_model m ON m.id = r.model_id
WHERE m.model = 'hr.employee.public'
""")
for row in env.cr.fetchall():
    print(row)
