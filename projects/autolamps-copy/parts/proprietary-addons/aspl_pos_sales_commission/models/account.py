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
from openerp.exceptions import Warning


class account_configuration(models.TransientModel):
    _inherit = 'account.config.settings'

    @api.multi
    def set_commission_account_id_defaults(self):
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'commission_account_id', self.commission_account_id.id or False)

    @api.multi
    def set_commission_pay_by_defaults(self):
        return self.env['ir.values'].sudo().set_default('account.config.settings', 'commission_pay_by', self.commission_pay_by or "")

    commission_account_id = fields.Many2one('account.account', string="Commission Account")
    commission_pay_by = fields.Selection([('invoice', 'Invoice'), ('salary', 'Salary')], string="Commission Pay By")


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    commission_invoice = fields.Boolean(string="Commission Invoice", copy=False)

    @api.multi
    def action_cancel(self):
        res = super(account_invoice, self).action_cancel()
        comm_obj = self.env['sales.commission']
        for invoice in self:
            if invoice.commission_invoice:
                comm_ids = comm_obj.search([('invoice_id', '=', invoice.id), ('state', 'not in', ['cancel', 'paid'])])
                comm_ids.write({'state': 'draft', 'invoice_id': False})
        return res

    @api.multi
    def action_cancel_draft(self):
        res = super(account_invoice, self).action_cancel_draft()
        comm_obj = self.env['sales.commission']
        for invoice in self:
            if invoice.commission_invoice:
                for line in invoice.invoice_line.filtered(lambda l: l.sale_commission_id):
                    if line.sale_commission_id.invoice_id:
                        raise Warning(_('Invoice cannot set as a Draft, because related commission lines assign to %s Invoice.') % (line.sale_commission_id.invoice_id.number or 'another'))
                    else:
                        if line.sale_commission_id.state == 'cancel':
                            raise Warning(_('Invoice cannot set as a Draft, because %s commission line is Cancelled.') % (line.sale_commission_id.name))
                        line.sale_commission_id.write({'state': 'invoiced', 'invoice_id': invoice.id})
        return True


class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'

    sale_commission_id = fields.Many2one('sales.commission', string="Sale Commission", readonly=True, copy=False)

    @api.multi
    def unlink(self):
        for line in self.filtered(lambda l:l.sale_commission_id):
            if line.sale_commission_id.invoice_id.id == line.invoice_id.id:
                line.sale_commission_id.write({'state': 'draft', 'invoice_id': False})
        return super(account_invoice_line, self).unlink()


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.multi
    def button_proforma_voucher(self):
        res = super(AccountVoucher, self).button_proforma_voucher()
        comm_obj = self.env['sales.commission']
        for rec in self:
            for line in rec.line_dr_ids:
                if line.move_line_id and line.move_line_id.invoice and line.move_line_id.invoice.commission_invoice and line.move_line_id.invoice.state == 'paid':
                    comm_obj.search([('invoice_id', '=', line.move_line_id.invoice.id)]).write({'state': 'paid'})
        return res


# class AccountPayment(models.Model):
#     _inherit = 'account.payment'
# 
#     @api.multi
#     def post(self):
#         super(AccountPayment, self).post()
#         comm_obj = self.env['sales.commission']
#         for rec in self:
#             for invoice in rec.invoice_ids:
#                 if invoice.commission_invoice and invoice.state == 'paid':
#                     comm_obj.search([('invoice_id', '=', invoice.id)]).write({'state': 'paid'})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: