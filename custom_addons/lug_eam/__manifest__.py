# -*- coding: utf-8 -*-

{

    "name": "Enterprise Asset Management (EAM)",

    "version": "19.0.2.0.0",

    "category": "Operations/Asset",

    "summary": "Quản lý tài sản: danh mục, vị trí, phiếu kho, bảo trì, KPI",

    "description": """

Enterprise Asset Management (lug_eam)

=====================================

- Master Data phân cấp (Category, Brand, Model, Location)

- Hồ sơ tài sản thống nhất + QR + vòng đời

- Phiếu kho tài sản (eam.transaction): nhập/xuất/chuyển/kiểm kê/thanh lý

- Bảo trì: chi phí, linh kiện, SLA, kiểm tra định kỳ

- Dashboard & KPI snapshot

- Custom trong app EAM, không ảnh hưởng module khác (R5)

    """,

    "author": "Custom",

    "license": "LGPL-3",

    "depends": [

        "base",

        "mail",

        "product",

        "stock",

        "maintenance",

        "hr",

        "lug_permission",

        "hr_employee_hrm_detail",

    ],

    "data": [

        "security/eam_security.xml",

        "security/ir.model.access.csv",

        "data/ir_sequence_data.xml",

        "data/eam_txn_sequence_data.xml",

        "data/eam_category_seed.xml",

        "data/ir_cron_data.xml",

        "data/lug_app_data.xml",

        "views/eam_brand_views.xml",

        "views/eam_model_views.xml",

        "views/eam_category_views.xml",

        "views/eam_location_views.xml",

        "views/maintenance_equipment_views.xml",

        "views/eam_transaction_views.xml",

        "views/eam_maintenance_views.xml",

        "views/eam_inspection_views.xml",

        "views/eam_asset_analysis_views.xml",

        "views/eam_asset_history_views.xml",

        "views/eam_operations_views.xml",

        "views/res_config_settings_views.xml",

        "report/eam_asset_label.xml",

        "views/eam_menus.xml",

    ],

    "installable": True,

    "application": True,

    "auto_install": False,

}


