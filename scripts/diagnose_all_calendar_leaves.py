# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

Leaves = env["resource.calendar.leaves"].sudo()
all_leaves = Leaves.search([])
print(f"ALL resource.calendar.leaves count={len(all_leaves)}")
for h in all_leaves[:30]:
    scope = getattr(h, "holiday_scope", "n/a")
    print(
        f"  id={h.id} res_id={h.resource_id.id if h.resource_id else None} "
        f"cal_id={h.calendar_id.id if h.calendar_id else None} "
        f"scope={scope} {h.date_from} | {h.name}"
    )
