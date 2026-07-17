# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
e2 = env["hr.employee"].sudo().browse(2)
print("e2", e2.name, "mien", e2.mien, "user_id", e2.user_id.id, "leave_manager", e2.leave_manager_id.id)
u58 = env["res.users"].browse(58)
print("leave_manager match", e2.leave_manager_id.id == 58)
print("user match", e2.user_id.id == 58)
