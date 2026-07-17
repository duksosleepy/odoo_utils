Leave = env["hr.leave"].__class__
names = [c.__name__ for c in Leave.mro()]
print("Lug in mro", "HrLeaveLugAccess" in names)
for n in names:
    if "Leave" in n or "Lug" in n:
        print(" ", n)
# which web_read
import inspect
for cls in Leave.mro():
    if "web_read" in cls.__dict__:
        print("web_read defined on", cls.__name__, cls.__module__)
