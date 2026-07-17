# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
cls = type(env["hr.employee.public"])
for c in cls.mro():
    if '_check_access' in c.__dict__ or 'web_read' in c.__dict__ or 'read' in c.__dict__:
        print(c.__module__.split('.')[-2] + '.' + c.__name__, 
              [m for m in ('read','web_read','_check_access') if m in c.__dict__])
