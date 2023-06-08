# -*- coding: utf-8 -*-

from openerp import models, fields, api

class CustomerCreditLimitApprovalTemplates(models.Model):

    _inherit = 'approval.template'
    
    document_type = fields.Selection(selection_add=[
        ('credit_limit',"Override Customer Credit Limit")
        ])

class CustomerCreditLimitApprovalRequest(models.Model):
    _inherit = 'approval.request'

    document_type = fields.Selection(selection_add=[
        ('credit_limit',"Override Customer Credit Limit")
        ])

    @api.model
    def create(self, vals):
        if vals['document_type'] == "credit_limit":
            messages = []
            order = self.env['sale.order'].search([('id','=',vals['document_id'])])
            for warning in order.warning_ids:
                messages.append((0, 0, {'name':warning.name}))
            if len(messages)>0:
                vals.update({'approval_message_ids':messages})

        return super(CustomerCreditLimitApprovalRequest, self).create(vals)

class CustomerCreditLimitApprovalRequestLines(models.Model):
    _inherit = 'approval.request.lines'

    document_type = fields.Selection(selection_add=[
        ('credit_limit',"Override Customer Credit Limit")
        ])

