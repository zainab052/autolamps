# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Website Backend Auto Operation(Order Confirmation/Invoice Generation/Invoice Payment)",
    "version" : "8.0.0.1",
    "price": 75,
    "currency": 'EUR',
    "category" : "eCommerce",
    "depends" : ['website','website_sale'],
    "author": "BrowseInfo",
    "summary": "This apps helps to generate auto backend( workflow when shop order proceed",
    "description": """
Odoo Website Sale.
    Website Auto Payment , Website Invoice Payment, Website Auto Invoice Payment, Website Auto Order Confirmation, Website Sale Confirmation, Website Order Auto Done, Website Order Auto paid, Invoice Paid from website, 
    Website Auto Confirm Quotation
    Website Auto Create Invoice
    Website Auto Validate Invoice
    Website Auto Create Payment
    Confirm Quotation
    Confirm Quotation And Create Invoice
    Confirm Quotation And Validate Invoice
    Confirm Quotation And Validate Invoice and Create Payment
    """,
    "website" : "https://www.browseinfo.in",
    "data": [
        'security/ir.model.access.csv',
        'views/template.xml',
    ],
    "auto_install": False,
    "application": True,
    "installable": True,
    'live_test_url':'https://youtu.be/go7x4blesSw',
    "images":['static/description/Banner.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
