# -*- coding: utf-8 -*-
u = env["res.users"].browse(85)
lug = u._lug_effective_permission_map()
print("lug perms", dict(lug))
print("target groups", [env["res.groups"].browse(g).name for g in u._lug_target_group_ids()])
print("has holidays_user", u.has_group("hr_holidays.group_hr_holidays_user"))
print("managed", u.has_group("hr_holidays.group_hr_holidays_user") and env.ref("hr_holidays.group_hr_holidays_user").id in env["res.users"]._lug_managed_group_ids())
