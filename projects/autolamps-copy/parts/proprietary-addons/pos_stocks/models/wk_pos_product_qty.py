# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)

class pos_config(osv.osv):
	_inherit = 'pos.config'
	
	_columns={
		'wk_display_stock': fields.boolean('Display stock in POS'),
		'wk_stock_type':fields.selection((('available_qty','Available Quantity(On hand)'),('forcated_qty','Forecasted Quantity'),('vartual_qty','Quantity on Hand - Outgoing Qty')),'Stock Type'),
		'wk_continous_sale':fields.boolean('Allow Order When Out-of-Stock'),
		'wk_deny_val': fields.integer('Deny order when product stock is lower than '),
		'wk_error_msg':fields.char('Custom message'),
		'wk_hide_out_of_stock':fields.boolean('Hide Out of Stock products')
	}
	_defaults = {
		'wk_deny_val': 0,
		'wk_stock_type':'available_qty',
		'wk_error_msg':'Out Of Stock'
	}

	