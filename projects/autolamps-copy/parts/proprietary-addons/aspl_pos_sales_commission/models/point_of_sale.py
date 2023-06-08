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

from openerp import models, fields, api, _
from lxml import etree
from openerp.osv.orm import setup_modifiers


class pos_order(models.Model):
    _inherit = 'pos.order'

    pos_sales_commission_line = fields.One2many('sales.commission', 'pos_order_id', string="Commission")
    commission_calculated = fields.Boolean(string="Commission Calculated", copy=False)

    @api.model
    def _mark_as_commission_calculated(self):
        old_pos_ids = self.search([('commission_calculated', '=', False)])
        old_pos_ids.write({'commission_calculated': True})


class pos_config(models.Model):
    _inherit = 'pos.config'

    comm_rule_group_id = fields.Many2one('commission.rule.group', string="Commission Rule Group")

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(pos_config, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                      submenu=submenu)
        if view_type == 'form':
            if not self.env.user.has_group('point_of_sale.group_pos_manager'):
                doc = etree.XML(res['arch'])
                if doc.xpath("//field[@name='comm_rule_group_id']"):
                    node = doc.xpath("//field[@name='comm_rule_group_id']")[0]
                    node.set('readonly', '1')
                    setup_modifiers(node, res['fields']['comm_rule_group_id'])
                res['arch'] = etree.tostring(doc)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: