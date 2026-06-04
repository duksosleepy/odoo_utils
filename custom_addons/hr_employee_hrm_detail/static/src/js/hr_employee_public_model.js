import { Record, fields } from "@mail/core/common/record";

/** Discuss persona: use public employee records (respects HR access rules). */
export class HrEmployeePublic extends Record {
    static _name = "hr.employee.public";
    static id = "id";

    id;
    company_id = fields.One("res.company");
    department_id = fields.One("hr.department");
    job_title;
    work_contact_id = fields.One("res.partner");
    user_id = fields.One("res.users");
    work_email;
    work_location_id = fields.One("hr.work.location");
    work_phone;
}

HrEmployeePublic.register();
