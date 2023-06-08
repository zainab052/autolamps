# -*- coding: utf-8 -*-
{
    'name': "Cash Management",

    'summary': """
        This module will be used to perform cash and bank transactions easily within Odoo
        """,

    'description': """
        This module contains documents used to perform cash transactions which include payment vouchers, receipts, imprest e.t.c
    """,

    'author': "Denis Korir",
    'website': "http://www.tritel.co.ke",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Cash Management',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'views/wizards.xml',
        'templates.xml',
        'views/cashmanagement_views.xml',
        'views/sequences.xml',
        'views/config.xml',
        'views/bi.xml',
        'views/workflows.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}
