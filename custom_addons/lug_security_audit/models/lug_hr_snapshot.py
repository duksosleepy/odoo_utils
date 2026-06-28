# -*- coding: utf-8 -*-


def job_title_label_from_employee(employee):
    """Resolve chức danh from hr.employee / hr.version fields."""
    if not employee:
        return False
    if "job_title" in employee._fields and employee.job_title:
        field = employee._fields["job_title"]
        value = employee.job_title
        if field.type == "selection":
            selection = field.selection
            if callable(selection):
                selection = selection(employee)
            return dict(selection).get(value, value)
        return value
    if employee.job_id:
        return employee.job_id.name
    return False
