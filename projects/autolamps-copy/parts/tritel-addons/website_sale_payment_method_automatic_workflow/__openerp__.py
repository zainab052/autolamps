# -*- coding: utf-8 -*-
{
    'name': 'Online Payment with direct invoice reconciliation',
    'version': '1.0',
    'category': 'Sale',
    'author':  'Jamotion GmbH',
    'website': 'https://jamotion.ch',
    'summary': 'Create payment move and reconciliate the corresponding invoice with it.',
    'images': ['static/description/all_together.png'],
    'depends': [
        'sale_payment_method_automatic_workflow',
        'payment',
    ],
    'data': [
        'views/payment_views.xml',
    ],
    'demo': [],
    'test': [],
    'application': False,
    'active': False,
    'installable': True,
}
