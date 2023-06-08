# -*- coding: utf-8 -*-
{
    'name': "Cash Management Approvals",

    'summary': """Approvals for Cash Management Module
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Dennis Korir",
    'website': "http://www.tritel.co.ke",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 
        'approvals',
        'cash_management',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
        'views/views.xml',
        'views/workflows.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}