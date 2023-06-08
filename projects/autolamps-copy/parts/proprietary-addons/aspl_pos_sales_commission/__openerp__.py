# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

{
    'name': 'POS Sales Commission',
    'summary': 'Commission to Sales Person',
    'version': '1.0',
    'description' :"""POS Sales Commission.""",
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'Point Of Sale',
    'website': "http://www.acespritech.com",
    'price': 35,
    'currency': 'EUR',
    'depends' : ['base', 'account', 'point_of_sale', 'hr_payroll'],
    'data' : [
        'security/security_view.xml',
        'security/ir.model.access.csv',
        'views/account_view.xml',
        'views/commission_rule_group_view.xml',
        'views/point_of_sale_view.xml',
        'views/sales_commission_view.xml',
        'wizard/sales_commission_payment_view.xml',
        'views/hr_payroll_data.xml',
        'views/hr_payroll_view.xml',
        'views/commission_scheduler.xml',
        'report/print_commission_summary_template.xml',
        'report/report.xml',
        'views/sales_target_view.xml'
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: 