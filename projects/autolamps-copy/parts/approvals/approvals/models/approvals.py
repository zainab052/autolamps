from openerp import fields,models,api
from openerp.exceptions import ValidationError
from datetime import datetime, timedelta
from lxml import etree
import simplejson
from urlparse import urljoin
from urllib import urlencode

class approval_template(models.Model):
    _name = 'approval.template' 

    name = fields.Char()
    description = fields.Text()
    document_type = fields.Selection([]) 
    limit_type = fields.Selection([('checker',"Checker"),('tiered',"Tiered")])
    enabled = fields.Boolean()
    enable_email_notifications = fields.Boolean('Use Mail Notifications')
    additional_approver_ids = fields.One2many('additional.approvers','template_id')
    default = fields.Boolean()
    approval_group_id = fields.Many2one('approval.groups', string = 'Grouping')

class additional_approvers(models.Model):
    _name = 'additional.approvers'
    _order = 'sequence, id asc'

    template_id = fields.Many2one('approval.template')
    approver_id = fields.Many2one('res.users', string = 'Approvers')
    sequence = fields.Integer() 
    minimum_amount = fields.Float()
    maximum_amount = fields.Float()

class ApprovalRequest(models.Model):
    _name = 'approval.request'
    _rec_name = 'no'
    _order = 'no desc'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    no = fields.Char()
    date = fields.Datetime(track_visibility='onchange')
    document_type = fields.Selection([], string = 'Document Type',track_visibility='onchange')
    model = fields.Char()
    document_id = fields.Integer(string = "Document ID")
    document_no = fields.Char(string = "Document No.", track_visibility='onchange')
    state = fields.Selection([
        ('open',"Open"),
        ('pending',"Pending Approval"),
        ('approved',"Approved"),
        ('rejected',"Rejected"),
        ('modify', "Modify")
        ], default = 'open', track_visibility='always')
    sender_id = fields.Many2one('res.users', string = "Sender")
    current_approver = fields.Many2one('res.users', string = "Approver", track_visibility='onchange')
    approval_request_line_ids = fields.One2many('approval.request.lines','approval_request_id')
    approved = fields.Boolean(default = False, track_visibility='onchange')
    rejected = fields.Boolean(default = False, track_visibility='onchange')
    approval_group_id = fields.Many2one('approval.groups', string = "Approval Group")
    comment_ids = fields.One2many('approval.comments', 'approval_request_id')
    comments_count = fields.Integer(compute = 'count_comments')
    company_id = fields.Many2one('res.company')
    user_modify = fields.Boolean(default = False, track_visibility='onchange')
    url = fields.Char()
    approval_message_ids = fields.One2many('approval.message','approval_request_id')

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'pending'),('current_approver','=',self.env.user.id)]

    @api.one
    @api.depends('comment_ids')
    def count_comments(self):
        self.comments_count = len(self.comment_ids)


    @api.one
    def get_sequence(self):
        res = self.env['ir.sequence'].search([('code', '=', 'approval.request')])
        sequence = self.env['ir.sequence'].search([('id', '=', res.id)])
        self.no = sequence.next_by_id(sequence.id, context=None)
        self.company_id = self.env.user.company_id.id 

    def get_signup_url(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        document = self.browse(cr, uid, ids[0], context=context)
        contex_signup = dict(context, signup_valid=True)
        return self.pool['res.partner']._get_signup_url_for_action(
            cr, uid, [document.current_approver.id], action='mail.action_mail_redirect',
            model=self._name, res_id=document.id, context=contex_signup,
        )[document.current_approver.id] 

    @api.one
    def get_url(self):
        document = self.browse(self.id)  
        res = False
        query = {'db':self._cr.dbname}
        fragment = {'action': 'approvals.approval_request_action','type': "signup",'view_type' : 'form','model' : 'approvals.approval.request','id': document.id,'login': document.current_approver.login}
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        res = urljoin(base_url, "?%s#%s" % (urlencode(query), urlencode(fragment)))
        self.url = res

    @api.multi
    def get_template(self):
        domain = [('document_type','=',self.document_type)]
        # add filter for approval groupings if provided by the approval request
        if self.approval_group_id != False:
            domain.append(('approval_group_id','=',self.approval_group_id.id))
        template = self.env['approval.template'].search(domain)
        if len(template)>1:
            domain.append(('default','=',True))
            template = self.env['approval.template'].search(domain)

        if len(template)>1:
            raise ValidationError("Multiple approval templates available for document type: %(document_type)s. Please make one a default approval template!" %{"document_type":self.document_type})
        elif len(template)==0:
            raise ValidationError("No approval template available for document type: %(document_type)s" %{"document_type":self.document_type})

        return template

    @api.one
    def get_approvers(self):
        template = self.get_template()
        existing_approvals = self.env['approval.request.lines'].search([
            ('document_type','=',self.document_type),
            ('document_id','=',self.document_id)
            ], order = 'sequence desc', limit = 1)
        if len(existing_approvals)==1:
            sequence = existing_approvals.sequence
        else:
            sequence = 0

        for approver in template.additional_approver_ids:
            sequence +=1
            self.env['approval.request.lines'].create({
                'approval_request_id':self.id,
                'approver_id':approver.approver_id.id,
                'sequence':sequence,
                'document_type':self.document_type,
                'document_id':self.document_id,
                'state':'open',
                'date_created':datetime.now()
                })

    @api.one
    def approve_request(self):
        approval_request_line = self.env['approval.request.lines'].search([
            ('approval_request_id','=',self.id),
            ('approver_id','=',self.current_approver.id),
            ('document_type','=',self.document_type),
            ('document_id','=',self.document_id),
            ('state','in',['open','pending'])
            ])
        if len(approval_request_line)>0:
            current_user = self.env.user
            if current_user.id != self.current_approver.id:
                raise ValidationError('You can only approve documents assigned to you!')
            else:
                approval_request_line.state = 'approved'
                approval_request_line.date_actioned = datetime.now()
                self.signal_workflow('pass_to_next_approver')


    @api.multi
    def show_approval_list(self):
        return {
            'type': 'ir.actions.act_window',
            'name': "Approval Requests",
            'res_model': "approval.request",
            # 'res_id':self.document_id,
            'view_type': 'tree',
            'view_mode': 'tree',
            'target': 'current',
        }

    
    @api.one
    def get_next_approver(self):
        next_approver = self.env['approval.request.lines'].search([
            ('approval_request_id','=',self.id),
            ('state','in',['open','pending'])
            ], order = 'sequence asc', limit = 1)
        if len(next_approver)==1:
            self.state = 'pending'
            next_approver.state = 'pending'
            self.current_approver = next_approver.approver_id.id
        else:
            self.current_approver = False
            self.approved = True


    @api.one
    def reject(self):
        self.rejected = True

    @api.one
    def modify(self):
        self.user_modify = True

    @api.one
    def mark_as_approved(self):
        self.state = 'approved'

    @api.one
    def mark_as_rejected(self):
        self.approval_request_line_ids.write({
            'state':'rejected',
            'date_actioned':datetime.now()
            })
        self.state = 'rejected'

    @api.one
    def mark_as_modified(self):
        self.approval_request_line_ids.write({
            'state': 'modify',
            'date_actioned': datetime.now()
        })
        self.state = 'modify'

    @api.one
    def notify(self):
        approval_template = self.get_template() 
        if approval_template.enable_email_notifications:
            template = self.env.ref('approvals.approval_request_notification')
            self.env['email.template'].browse(
                template.id).send_mail(self.id) #, force_send=True

    @api.one
    def notify_accept_approval(self):
        approval_template = self.get_template() 
        if approval_template.enable_email_notifications:
            template = self.env.ref('approvals.approval_accept_notification')
            self.env['email.template'].browse(
                template.id).send_mail(self.id)

    @api.one
    def notify_modify_approval(self):
        approval_template = self.get_template() 
        if approval_template.enable_email_notifications:
            template = self.env.ref('approvals.approval_modify_notification')
            self.env['email.template'].browse(
                template.id).send_mail(self.id)

    @api.one
    def notify_reject_approval(self):
        approval_template = self.get_template() 
        if approval_template.enable_email_notifications:
            template = self.env.ref('approvals.approval_rejection_notification')
            self.env['email.template'].browse(
                template.id).send_mail(self.id)

    @api.multi
    def show_document(self):
        return {
            'type': 'ir.actions.act_window',
            'name': self.document_type,
            'res_model': self.model,
            'res_id':self.document_id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        context = self._context
        res = super(ApprovalRequest, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
           submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type == 'form':            # Applies only for form view
            for node in doc.xpath("//field"):   # All the view fields to readonly
                node.set('readonly', '1')
                node.set('modifiers', simplejson.dumps({"readonly": True}))

        res['arch'] = etree.tostring(doc)
        
        return res


class approval_request_lines(models.Model):
    _name = 'approval.request.lines'
    _order = 'sequence asc'

    approval_request_id = fields.Many2one('approval.request')
    approver_id = fields.Many2one('res.users', string = 'Approver')
    sequence = fields.Integer()
    document_type = fields.Selection([])
    document_id = fields.Integer(string = "Document Id")
    state = fields.Selection([
        ('open',"Open"),
        ('pending',"Pending Approval"),
        ('approved',"Approved"),
        ('rejected',"Rejected"),
        ('modify',"Modify")
        ], default = 'open')
    date_created = fields.Datetime()
    date_actioned = fields.Datetime()
    comment_ids = fields.One2many('approval.comments','approval_request_line_id')
    comments_count = fields.Integer(compute = 'count_comments')

    @api.one
    @api.depends('comment_ids')
    def count_comments(self):
        self.comments_count = len(self.comment_ids)

class ApprovalComments(models.Model):
    _name = 'approval.comments'

    approval_request_id = fields.Many2one('approval.request', string = 'Approval Request')
    approval_request_line_id = fields.Many2one('approval.request.lines')
    approver_id = fields.Many2one('res.users', string = 'Approver')
    comment = fields.Text()
    date = fields.Datetime()

class approval_setup(models.Model):
    _name = 'approval.setup' 

    name = fields.Char()
    approval_numbers = fields.Many2one('ir.sequence', default = '_default_approval_numbers')


    @api.one
    def set_approval_number(self):
        res = self.env['ir.sequence'].search([('code', '=', 'approval.request')])
        self.approval_numbers = res.id

    @api.model
    def _default_approval_numbers(self):
        res = self.env['ir.sequence'].search([('code','=','approval.request')])
        return res.id or 1

class approval_settings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'approvals.config.settings'

    default_approval_numbers = fields.Char(default_model='approval.setup')

class ApprovalGrouping(models.Model):
    _name = 'approval.groups'

    name = fields.Char()

class ApprovalMessages(models.Model):
    _name = 'approval.message'

    approval_request_id = fields.Many2one('approval.request')
    name = fields.Char(string="Messages")
