# -*- coding: utf-8 -*-
{
    'name': 'HR Mã Kho',
    'version': '19.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Quản lý danh mục mã kho',
    'depends': ['hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_kho_views.xml',
        'views/hr_kho_menus.xml',
    ],
    'license': 'LGPL-3',
    'author': 'Custom',
    'installable': True,
    'application': False,
}
