# -*- coding: utf-8 -*-

from openerp import models, fields, api

class cash_management_approval_templates(models.Model):

    _inherit = 'approval.template'
    
    document_type = fields.Selection(selection_add=[
    	('petty_cash',"Petty Cash Requisition"),
    	('payment_voucher',"Payment Vouchers"),
        ('claim',"Staff Claim"),
        ('cash_transfer',"Bank & Cash Transfers")
    	])

class cash_management_approval_request(models.Model):
    _inherit = 'approval.request'

    document_type = fields.Selection(selection_add=[
    	('petty_cash',"Petty Cash Requisition"),
    	('payment_voucher',"Payment Vouchers"),
        ('claim',"Staff Claim"),
        ('cash_transfer',"Bank & Cash Transfers")
    	])

class cash_management_approval_request_lines(models.Model):
    _inherit = 'approval.request.lines'

    document_type = fields.Selection(selection_add=[
    	('petty_cash',"Petty Cash Requisition"),
    	('payment_voucher',"Payment Vouchers"),
        ('claim',"Staff Claim"),
        ('cash_transfer',"Bank & Cash Transfers")
    	])

