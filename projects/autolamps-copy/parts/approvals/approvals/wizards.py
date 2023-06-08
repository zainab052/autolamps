from openerp import fields, models, api
from openerp.exceptions import ValidationError
from datetime import datetime, timedelta

class ApprovalCommentWizard(models.TransientModel):
    _name = 'approval.comment.wizard'

    approval_request_id = fields.Many2one('approval.request')
    approver_id = fields.Many2one('res.users')
    comment = fields.Text(required = True)
    date = fields.Date(default = fields.Date.today)

    @api.one
    def modify(self):
    	approval_request_line = self.env['approval.request.lines'].search([
    		('approval_request_id','=',self.approval_request_id.id),
    		('approver_id','=',self.approver_id.id)
    		])
    	comment = self.env['approval.comments'].create({
    		'approval_request_id':self.approval_request_id.id,
    		'approval_request_line_id':approval_request_line.id,
    		'approver_id':self.approver_id.id,
    		'comment':self.comment,
    		'date':datetime.now()
    		})
    	self.approval_request_id.modify()

    @api.one
    def reject(self):
        approval_request_line = self.env['approval.request.lines'].search([
            ('approval_request_id','=',self.approval_request_id.id),
            ('approver_id','=',self.approver_id.id)
            ])
        comment = self.env['approval.comments'].create({
            'approval_request_id':self.approval_request_id.id,
            'approval_request_line_id':approval_request_line.id,
            'approver_id':self.approver_id.id,
            'comment':self.comment,
            'date':datetime.now()
            })
        self.approval_request_id.reject()