# -*- coding: utf-8 -*-
import sys
from inspect import getmembers
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

cls = env.registry["resource.calendar.leaves"]
for attr, func in getmembers(cls, lambda f: callable(f) and hasattr(f, "_constrains")):
    fields = getattr(func, "_constrains", ())
    if "date_from" in fields:
        print("constraint:", attr, func.__qualname__, fields)
        try:
            src = func.__code__.co_filename
        except AttributeError:
            src = getattr(func, "__wrapped__", func)
            src = getattr(src, "__code__", None)
            src = src.co_filename if src else "?"
        print("  file:", src)
