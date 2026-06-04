import { ResPartner } from "@mail/core/common/res_partner_model";
import { ResUsers } from "@mail/core/common/res_users_model";
import { fields } from "@mail/model/misc";
import { patch } from "@web/core/utils/patch";
import { user } from "@web/core/user";

/** Load discuss personas via hr.employee.public to avoid hr.employee ACL errors. */
patch(ResPartner.prototype, {
    setup() {
        super.setup();
        this.employee_ids = fields.Many("hr.employee.public", {
            inverse: "work_contact_id",
        });
        this.employee_id = fields.One("hr.employee.public", {
            compute() {
                return (
                    this.employee_ids.find(
                        (employee) => employee.company_id?.id === user.activeCompany.id
                    ) || this.employee_ids[0]
                );
            },
        });
    },
});

patch(ResUsers.prototype, {
    setup() {
        super.setup();
        this.employee_ids = fields.Many("hr.employee.public", {
            inverse: "user_id",
        });
        this.employee_id = fields.One("hr.employee.public", {
            compute() {
                return (
                    this.employee_ids.find(
                        (employee) => employee.company_id?.id === user.activeCompany.id
                    ) || this.employee_ids[0]
                );
            },
        });
    },
});
