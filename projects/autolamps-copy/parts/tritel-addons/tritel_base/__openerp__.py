# -*- coding: utf-8 -*-
{
    'name': "Tritel Base",
    'summary': """
        Tritel Base Module -  Adds security features to Odoo
        """,
    'description': """
        - Adds contact creation security group
        - Adds product creation security group
     """,
    'author': "Tritel Technologies Ltd",
    'website': "http://www.tritel.co.ke",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
            'base',
            'product'
        ],
    'data': [
        "security/res_groups.xml",
        "security/product_groups.xml",
        "security/res_partner_groups.xml",
        "security/ir.model.access.csv",
        ],
}
