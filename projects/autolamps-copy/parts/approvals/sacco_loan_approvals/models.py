# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta

class sacco_approval_templates(models.Model):

    _inherit = 'approval.template'
    
    document_type = fields.Selection(selection_add=[('loan',"Loan Application")])

class sacco_approval_request(models.Model):
    _inherit = 'approval.request'

    document_type = fields.Selection(selection_add=[('loan',"Loan Application")])

class sacco_approval_request_lines(models.Model):
    _inherit = 'approval.request.lines'

    document_type = fields.Selection(selection_add=[('loan',"Loan Application")])

class SaccoLoanProductType(models.Model):
    _inherit = 'sacco.loan.types'

    approval_group_id = fields.Many2one('approval.groups', string = 'Approval Group')
    

class sacco_loan(models.Model):
    _inherit = 'sacco.loan'

    approval_entries = fields.Integer(compute = 'count_approvers')

    @api.one
    @api.depends('name')
    def count_approvers(self):
        approvers = self.env['approval.request.lines'].search([
            ('document_type','=','loan'),
            ('document_id','=',self.id),
            ('state','in',['open','pending','approved'])
            ])
        self.approval_entries = len(approvers)

    @api.multi
    def send_approval_request(self):
        approval_request = self.env['approval.request'].create({
            'date':datetime.now(),
            'document_type':'loan',
            'model':'sacco.loan',
            'document_id':self.id,
            'document_no':self.name,
            'sender_id':self.env.user.id,
            'approval_group_id':self.loan_product_type.approval_group_id.id
            })
        approval_request.signal_workflow('send_approval_request')
        return approval_request.id 

    @api.multi
    def test_state(self):
        approval_request = self.env['approval.request'].search([
            ('model','=','sacco.loan'),
            ('document_id','=',self.id),
            ('document_no','=',self.name)
            ], order = 'date desc', limit = 1)
        if len(approval_request)==1:
            if approval_request.state == 'approved':
                return True
            else:
                return False   

    @api.multi
    def approval_request_get(self):
        res = [] 
        approval_request = self.env['approval.request'].search([
            ('model','=','sacco.loan'),
            ('document_id','=',self.id),
            ('document_no','=',self.name)
            ], order = 'date desc', limit = 1) 
        if len(approval_request)==1:
            res.append(approval_request.id) 

        return res      