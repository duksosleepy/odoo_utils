# -*- coding: utf-8 -*-

def post_init_hook(env):
    env['hr.employee.operation.log']._backfill_change_summaries()
