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

from openerp import models, fields, api
from lxml import etree


class SalesCommission(models.Model):
    _name = 'sales.commission'
    _order = 'order_date desc'

    @api.one
    def state_cancel(self):
        if self.state == 'draft' and not self.invoice_id:
            self.state = 'cancel'

    @api.one
    def set_to_draft(self):
        self.write({'state': 'draft'})

    @api.model
    def generate_commission_invoice(self):
        sale_comm_pay_obj = self.env['sales.commission.payment'].create({'all_user': True}).generate_invoice()

    name = fields.Char(string="Source Document")
    pos_order_id = fields.Many2one('pos.order', string="POS Order")
    user_sales_amount = fields.Float(string="Sales Amount")
    user_id = fields.Many2one('res.users', string="User")
    job_id = fields.Many2one('hr.job', string="Job Position")
    order_date = fields.Date(string="Order Date")
    amount = fields.Float(string="Commission Amount")
    pay_by = fields.Selection([('salary', 'Salary'), ('invoice', 'Invoice')], string="Pay By", default="invoice")
    state = fields.Selection([('draft', 'Draft'), ('invoiced', 'Invoiced'), ('paid', 'Paid'),
                              ('cancel', 'Cancel')], string="Status", default='draft')
    invoice_id = fields.Many2one('account.invoice', string="Invoice")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: