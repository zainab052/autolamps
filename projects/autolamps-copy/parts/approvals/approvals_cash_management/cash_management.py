from openerp import models, fields, api
from datetime import datetime, timedelta

class PettyCashHeaderApproval(models.Model):
    _inherit = 'cash.management.petty.cash.header'

    approval_entries = fields.Integer(compute = 'count_approvers')
    state = fields.Selection([
        ('draft',"Draft"),
        ('pending',"Pending Approval"),
        ('approved',"Approved"),
        ('complete',"Complete"),
        ('rejected',"Rejected")
        ], default = 'draft') 

    @api.one
    @api.depends('name')
    def count_approvers(self):
        approvers = self.env['approval.request.lines'].search([
            ('document_type','=','petty_cash'),
            ('document_id','=',self.id),
            ('state','in',['open','pending','approved'])
            ])
        self.approval_entries = len(approvers)

    @api.one
    def mark_as_pending_approval(self):
        self.state = 'pending'

    @api.one
    def mark_as_approved(self):
        self.state = 'approved'

    @api.one
    def mark_as_rejected(self):
        self.state = 'rejected'

    @api.multi
    def send_approval_request(self):
        approval_request = self.env['approval.request'].create({
            'date':datetime.now(),
            'document_type':'petty_cash',
            'model':'cash.management.petty.cash.header',
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
            ('model','=','cash.management.petty.cash.header'),
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
            ('model','=','cash.management.petty.cash.header'),
            ('document_id','=',self.id),
            ('document_no','=',self.name)
            ], order = 'date desc', limit = 1)
        if len(approval_request)==1:
            res.append(approval_request.id)
        return res

class PaymentVoucherApprovals(models.Model):
    _inherit = 'cash.management.payment.header'

    approval_entries = fields.Integer(compute = 'count_approvers')
    state = fields.Selection([
        ('draft',"Draft"),
        ('pending',"Pending Approval"),
        ('approved',"Approved"),
        ('complete',"Complete"),
        ('rejected',"Rejected")
        ], default = 'draft') 

    @api.one
    @api.depends('name')
    def count_approvers(self):
        approvers = self.env['approval.request.lines'].search([
            ('document_type','=','payment_voucher'),
            ('document_id','=',self.id),
            ('state','in',['open','pending','approved'])
            ])
        self.approval_entries = len(approvers)

    @api.one
    def mark_as_pending_approval(self):
        self.state = 'pending'

    @api.one
    def mark_as_approved(self):
        self.state = 'approved'

    @api.one
    def mark_as_rejected(self):
        self.state = 'rejected'

    @api.multi
    def send_approval_request(self):
        approval_request = self.env['approval.request'].create({
            'date':datetime.now(),
            'document_type':'payment_voucher',
            'model':'cash.management.payment.header',
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
            ('model','=','cash.management.payment.header'),
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
            ('model','=','cash.management.payment.header'),
            ('document_id','=',self.id),
            ('document_no','=',self.name)
            ], order = 'date desc', limit = 1)
        if len(approval_request)==1:
            res.append(approval_request.id)
        return res

class StaffClaimApprovals(models.Model):
    _inherit = 'cash.management.staff.claim'

    approval_entries = fields.Integer(compute = 'count_approvers')
    state = fields.Selection([
        ('draft',"Draft"),
        ('pending',"Pending Approval"),
        ('approved',"Approved"),
        ('open',"Open"),
        ('complete',"Claimed"),
        ('rejected',"Rejected")
        ], default = 'draft') 

    @api.one
    @api.depends('name')
    def count_approvers(self):
        approvers = self.env['approval.request.lines'].search([
            ('document_type','=','claim'),
            ('document_id','=',self.id),
            ('state','in',['open','pending','approved'])
            ])
        self.approval_entries = len(approvers)

    @api.one
    def mark_as_pending_approval(self):
        self.state = 'pending'

    @api.one
    def mark_as_approved(self):
        self.state = 'approved'

    @api.one
    def mark_as_rejected(self):
        self.state = 'rejected'

    @api.multi
    def send_approval_request(self):
        approval_request = self.env['approval.request'].create({
            'date':datetime.now(),
            'document_type':'claim',
            'model':'cash.management.staff.claim',
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
            ('model','=','cash.management.staff.claim'),
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
            ('model','=','cash.management.staff.claim'),
            ('document_id','=',self.id),
            ('document_no','=',self.name)
            ], order = 'date desc', limit = 1)
        if len(approval_request)==1:
            res.append(approval_request.id)
        return res

class CashTransferApproval(models.Model):
    _inherit = 'cash.management.bank.transfer.header'

    approval_entries = fields.Integer(compute = 'count_approvers')
    state = fields.Selection([
        ('draft',"Draft"),
        ('pending',"Pending Approval"),
        ('approved',"Approved"),
        ('complete',"Complete"),
        ('rejected',"Rejected")
        ], default = 'draft') 

    @api.one
    @api.depends('name')
    def count_approvers(self):
        approvers = self.env['approval.request.lines'].search([
            ('document_type','=','cash_transfer'),
            ('document_id','=',self.id),
            ('state','in',['open','pending','approved'])
            ])
        self.approval_entries = len(approvers)

    @api.one
    def mark_as_pending_approval(self):
        self.state = 'pending'

    @api.one
    def mark_as_approved(self):
        self.state = 'approved'

    @api.one
    def mark_as_rejected(self):
        self.state = 'rejected'

    @api.multi
    def send_approval_request(self):
        approval_request = self.env['approval.request'].create({
            'date':datetime.now(),
            'document_type':'cash_transfer',
            'model':'cash.management.bank.transfer.header',
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
            ('model','=','cash.management.bank.transfer.header'),
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
            ('model','=','cash.management.bank.transfer.header'),
            ('document_id','=',self.id),
            ('document_no','=',self.name)
            ], order = 'date desc', limit = 1)
        if len(approval_request)==1:
            res.append(approval_request.id)
        return res 