{
    'name': 'Sold Out Functionality Odoo',
    'version': '1.0',
    'description': "",
    'category': 'Generic Modules',
	'website': 'http://www.o2b.co.in',
    'author': 'O2B Technologies',
    'depends': ['product','website_sale'],
    'summary': "This functionality will help users to show Product on the eCommerce store even if they dont want to sell that product",
    'data':['product_template.xml',
            'template.xml',
    ],
    'images': [
        'static/description/icon.png'
    ],
    'installable': True,
    'active': False,
  }