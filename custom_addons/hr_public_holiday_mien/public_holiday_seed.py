# -*- coding: utf-8 -*-

HOLIDAY_SCOPE_VP = "vp"

# Default VN public holidays (2026) — only inserted when DB has none yet.
DEFAULT_PUBLIC_HOLIDAYS_2026 = [
    {
        "name": "Quốc tế Lao động năm 2026 (30/4 - 1/5)",
        "date_from": "2026-04-29 17:00:00",
        "date_to": "2026-05-01 16:59:59",
    },
    {
        "name": "Tết Nguyên đán",
        "date_from": "2026-05-26 17:00:00",
        "date_to": "2026-05-27 16:59:59",
    },
    {
        "name": "Tết dương lịch",
        "date_from": "2026-06-26 17:00:00",
        "date_to": "2026-06-29 16:59:59",
    },
    {
        "name": "Lễ Quốc Khánh 2026 (2/9)",
        "date_from": "2026-09-01 17:00:00",
        "date_to": "2026-09-03 16:59:59",
    },
    {
        "name": "Ngày Văn hóa Việt Nam",
        "date_from": "2026-11-23 17:00:00",
        "date_to": "2026-11-24 16:59:59",
    },
]


def seed_public_holidays_if_empty(env):
    """Create default VP public holidays when the database has none configured."""
    Leaves = env["resource.calendar.leaves"].sudo()
    if Leaves.search_count([("resource_id", "=", False)]):
        return 0
    company = env.company
    created = 0
    for vals in DEFAULT_PUBLIC_HOLIDAYS_2026:
        Leaves.create(
            {
                **vals,
                "resource_id": False,
                "calendar_id": False,
                "company_id": company.id,
                "holiday_scope": HOLIDAY_SCOPE_VP,
            }
        )
        created += 1
    return created
