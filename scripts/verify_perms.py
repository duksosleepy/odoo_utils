with open(r"d:\Lap_odoo\odoo_time_off_custom\scripts\verify_perms_out.txt", "w", encoding="utf-8") as f:
    for login in ["anh.trinh@sangtam.com", "admin.lug@sangtam.com"]:
        u = env["res.users"].sudo().search([("login", "=", login)], limit=1)
        if not u:
            f.write("%s NOT FOUND\n" % login)
            continue
        miens = u._hr_leave_analytics_allowed_miens_list()
        groups = [g.name for g in u.group_ids if g.name and "Báo cáo nghỉ phép" in g.name]
        f.write("%s miens=%s groups=%s\n" % (login, miens, groups))
