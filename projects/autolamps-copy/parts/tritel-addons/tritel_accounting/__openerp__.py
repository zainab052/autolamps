# -*- coding: utf-8 -*-
{
    'name': "tritel_accounting",

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
    'category': 'Accounting',
    'version': '8.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'l10n_ke',
        'report_xlsx',
        ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/account.tax.code.csv',
        'data/account.tax.csv',
        'report/report_vat.xml',
        'views/res_currency.xml',
        'wizards/vat.xml',
    ],
}