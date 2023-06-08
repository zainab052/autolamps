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
    'name': 'POS Pricelist',
    'description': "Apply pricelist from Point Of Sale Interface",
    'author': "Acespritech Solutions Pvt. Ltd.",
    'summary': 'Apply pricelist from Point Of Sale Interface',
    'version': '1.0',
    'website': "http://www.acespritech.com",
    'category': 'Point of Sale',
    'price': 12,
    'currency': 'EUR',
    'images': ['static/description/main_screenshot.png'],
    'depends': ['base','sale','point_of_sale', 'pos_stocks'],
    'data': [
        'views/template.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
    'auto_install': False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
