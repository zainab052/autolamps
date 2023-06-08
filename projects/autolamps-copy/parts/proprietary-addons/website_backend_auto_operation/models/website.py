# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from openerp import fields, models, api, _
from openerp import SUPERUSER_ID

class website_config_settings(models.Model):
    _inherit = 'website.config.settings'
    
    website_order_configuration = fields.Selection([ ('confirm', 'Confirm Quotation'),
    ('invoice', 'Confirm Quotation and Create Invoice'),
    ('validate', 'Confirm Quotation and Validate Invoice'),
    ('payment', 'Confirm Quotation, Validate Invoice and Create Payment')], string="Website Order Configuration")


    @api.model
    def default_get(self, fields_list):
        res = super(website_config_settings, self).default_get(fields_list)
        if self.search([], limit=1, order="id desc").website_order_configuration:
            res.update({'website_order_configuration': self.search([], limit=1, order="id desc").website_order_configuration})
            
        return res

class payment_acquirer(models.Model):
    _inherit = 'payment.acquirer'
    
    journal_id = fields.Many2one('account.journal', 'Journal')
    
    website_order_msg = fields.Selection([ ('confirm', 'Confirm Quotation'),
    ('invoice', 'Create Invoice'),
    ('validate', 'Validate Invoice'),
    ('payment', 'Create Payment')], string="Website Order Configuration")
    
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
