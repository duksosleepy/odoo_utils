# -*- coding: utf-8 -*-
Employee = env["hr.employee"]
for cls in Employee.__class__.mro():
    if "write" in cls.__dict__ and cls.__name__ != "BaseModel":
        print(cls.__module__.split(".")[-2] + "." + cls.__name__)
