# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

u85 = env["res.users"].browse(85)
Emp = env["hr.employee"].with_user(u85)
Pub = env["hr.employee.public"].with_user(u85)

def find_failing_field(Model, rec_id, label):
    print(f"\n=== {label} emp {rec_id} ===")
    fields = list(Model._fields.keys())
    # batch binary search
    def test(fnames):
        spec = {f: {} for f in fnames}
        try:
            Model.browse(rec_id).web_read(spec)
            return True, None
        except Exception as ex:
            return False, ex
    failing = []
    for fname in fields:
        field = Model._fields[fname]
        if field.type in ("one2many", "many2many"):
            continue
        if field.groups and not u85.has_groups(field.groups):
            continue
        ok, ex = test([fname])
        if not ok:
            failing.append((fname, str(ex)[:150]))
    print("failing scalar fields", len(failing))
    for f, msg in failing[:20]:
        print(" ", f, msg)

find_failing_field(Emp, 8, "hr.employee")
find_failing_field(Emp, 71, "hr.employee")
find_failing_field(Pub, 8, "hr.employee.public")
find_failing_field(Pub, 71, "hr.employee.public")
