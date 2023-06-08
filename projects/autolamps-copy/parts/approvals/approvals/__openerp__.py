# -*- coding: utf-8 -*-
{
    'name': "Approvals",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Tritel Technologies Ltd",
    'website': "http://www.tritel.co.ke",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Approvals',
    'version': '8.0',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','account'],

    # always loaded
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'templates.xml',
        'views/wizards.xml',
        'views/approvals.xml',
        'data/default_data.xml',
        'data/sequences.xml',
        'views/workflows.xml',
        'data/email_template.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}