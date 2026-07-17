# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
cls = type(env["hr.employee"])
for c in cls.mro():
    if 'web_read' in c.__dict__:
        print(c.__module__, c.__name__)
