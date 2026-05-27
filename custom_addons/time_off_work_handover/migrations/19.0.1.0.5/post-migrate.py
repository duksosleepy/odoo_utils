from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    rule = env.ref("hr_holidays.hr_holidays_status_rule_multi_company", raise_if_not_found=False)
    if not rule:
        return
    rule.write(
        {
            "domain_force": """[
                '|',
                    ('company_id', 'in', company_ids),
                    ('company_id', '=', False)
            ]"""
        }
    )
