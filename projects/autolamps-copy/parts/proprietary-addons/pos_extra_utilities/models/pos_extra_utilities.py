# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from openerp.osv import fields, osv
from openerp import api

class pos_config(osv.osv):
	_inherit = 'pos.config'
	_columns = {
		'disable_price_modification': fields.boolean("Disable price modification"),
		'allow_only_price_increase': fields.boolean("Allow only increase in price"),
		'disable_discount_button': fields.boolean("Disable discounts"),
		'disable_delete_button': fields.boolean("Disable delete"),
		'validation_check': fields.boolean("Do not validate order if customer is not selected"),
	}