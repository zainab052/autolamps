#-*- coding:utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import datetime, timedelta
from collections import defaultdict


class sale_order(models.Model):
    _inherit = "sale.order"

    approval_entries = fields.Integer(compute = 'count_approvers') 
    warning_ids = fields.One2many('sale.approval.warnings', 'sale_id', string="Warnings")
    state = fields.Selection([
            ('draft', 'Draft Quotation'),
            ('sent', 'Quotation Sent'),
            ('approval',"Limit Approval"),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('progress', 'Sales Order'),
            ('manual', 'Sale to Invoice'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True)

    @api.one
    @api.depends('name')
    def count_approvers(self):
        approvers = self.env['approval.request.lines'].search([
            ('document_type','=','credit_limit'),
            ('document_id','=',self.id),
            ('state','in',['open','pending','approved','modify'])
            ])
        self.approval_entries = len(approvers)

    @api.multi
    def mark_as_draft(self):
        self.state = 'draft'


    @api.multi
    def mark_as_pending_approval(self):
        self.state = 'approval' 

    @api.multi
    def send_approval_request(self):
        approval_request = self.env['approval.request'].create({
            'date':datetime.now(),
            'document_type':'credit_limit',
            'model':'sale.order',
            'document_id':self.id,
            'document_no':self.name,
            'sender_id':self.env.user.id 
            # 'approval_group_id':self.loan_product_type.approval_group_id.id
            })
        approval_request.signal_workflow('send_approval_request')
        return approval_request.id

    @api.multi
    def test_state(self):
        approval_request = self.env['approval.request'].search([
            ('model','=','sale.order'),
            ('document_id','=',self.id),
            ('document_no','=',self.name)
            ], order = 'date desc', limit = 1)
        if len(approval_request)==1:
            if approval_request.state == 'approved':
                return True
            else:
                return False
        else: 
            return False   

    @api.multi
    def approval_request_get(self):
        res = [] 
        approval_request = self.env['approval.request'].search([
            ('model','=','sale.order'),
            ('document_id','=',self.id),
            ('document_no','=',self.name)
            ], order = 'date desc', limit = 1)
        if len(approval_request)==1:
            res.append(approval_request.id)
        return res

    @api.multi
    def sale_order_get(self):
    	res = [self.id]
        return res


    @api.multi
    def check_limit(self):
        # check and return true if sale is from e-commerce
        if self.payment_tx_id:
            return True
            
        warnings = []
        self.warning_ids.unlink()

        if self.order_policy == 'prepaid':
            return True

        # We sum from all the sale orders that are aproved, the sale order
        # lines that are not yet invoiced
        domain = [('order_id.partner_id', '=', self.partner_id.id),
                  ('invoiced', '=', False),
                  ('order_id.state', 'not in', ['draft', 'cancel', 'sent'])]
        order_lines = self.env['sale.order.line'].search(domain)
        none_invoiced_amount = sum([x.price_subtotal for x in order_lines])

        # We sum from all the invoices that are in draft the total amount
        domain = [
            ('partner_id', '=', self.partner_id.id), ('state', '=', 'draft')]
        draft_invoices = self.env['account.invoice'].search(domain)
        draft_invoices_amount = sum([x.amount_total for x in draft_invoices])

        available_credit = self.partner_id.credit_limit - \
            self.partner_id.credit - \
            none_invoiced_amount - draft_invoices_amount
        
        # limit check
        limit = True
        if self.partner_id.credit_limit > 0:
            if self.amount_total > available_credit:
                # append warnings and return false
                warnings.append((0, 0, {'name':'Credit Limit Exceeded'}))
                limit = False

        # credit violation check
        credit = True
        company_id = self.env.user.company_id.id
        lines_per_currency = defaultdict(list)
        movelines = self.env['account.move.line'].search([
                            ('partner_id', '=', self.partner_id.id),
                            ('account_id.type', '=', 'receivable'),
                            ('reconcile_id', '=', False),
                            ('state', '!=', 'draft'),
                            ('company_id', '=', company_id),
                            '|', ('date_maturity', '=', False), ('date_maturity', '<=', fields.Date.context_today(self)),
                        ])

        for line in movelines:
            currency = line.currency_id or line.company_id.currency_id
            line_data = {
                'name': line.move_id.name,
                'ref': line.ref,
                'date': line.date,
                'date_maturity': line.date_maturity,
                'balance': line.amount_currency if currency != line.company_id.currency_id else line.debit - line.credit,
                'blocked': line.blocked,
                'currency_id': currency,
            }
            lines_per_currency[currency].append(line_data)

        currency_balances = [{'balance': sum(line['balance'] for line in lines), 'currency': currency} for currency, lines in lines_per_currency.items()]

        for item in currency_balances:
            if item['balance'] > 0:
                warnings.append((0, 0, {'name': 'Credit Period Violated with Overdue %s : %s' %(item['currency']['name'], item['balance'])}))
                credit = False

        if len(warnings)>0:
            self.warning_ids = warnings

        return limit and credit #returns true if both are ok else false
        
        # return True #always return true if no credit limits are set and no due dates are violated

class SaleApprovalWarnings(models.Model):
    _name = 'sale.approval.warnings'

    sale_id = fields.Many2one('sale.order') 
    name = fields.Char(string='Warnings')