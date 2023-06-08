# -*- coding: utf-8 -*-
{
    'name': "Customer Credit Limit Approvals",

    'summary': """
        Approvals routine that allows adding of approvals to override credit limits
        set on customer details""",

    'description': """
        Approvals routine that allows adding of approvals to override credit limits
        set on customer details
    """,

    'author': "Tritel Technologies Ltd",
    'website': "http://www.tritel.co.ke",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Approvals',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','approvals'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'templates.xml',
        'views/approvals.xml',
        'views/sale_workflows.xml',
        'views/sale.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}