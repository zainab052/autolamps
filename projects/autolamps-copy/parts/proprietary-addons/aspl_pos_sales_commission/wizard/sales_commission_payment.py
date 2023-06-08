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
from datetime import datetime


class SalesCommissionPayment(models.TransientModel):
    _name = 'sales.commission.payment'

    @api.multi
    def generate_invoice(self):
        invoice_obj = self.env['account.invoice']
        scobj = self.env['sales.commission']
        user_obj = self.env['res.users']
        domain = [('state', '=', 'draft'), ('pay_by', '=', 'invoice'),
                  '|', ('invoice_id', '=', False), ('invoice_id.state', '=', 'cancel')]
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise Warning(_('End Date should be greater than Start Date.'))
            domain.append(('order_date', '>=', self.start_date))
            domain.append(('order_date', '<=', self.end_date))
        else:
            domain.append(('order_date', '<=', self.end_date or fields.Date.today()))
        users = user_obj.search([]) if self.all_user else self.user_ids
        domain.append(('user_id', 'in', [user.id for user in users]))
        commission_ids = scobj.search(domain)
        if not commission_ids:
            return True
        journal_id = invoice_obj.with_context({'type': 'in_invoice', 'journal_type': 'purchase',
                                               'company_id': self.env.user.company_id.id})._default_journal()
        if not journal_id:
            raise Warning(_('Account Journal not found.'))
        commission_account_id = self.env['ir.values'].sudo().get_default('account.config.settings', 'commission_account_id')
        if not commission_account_id:
            raise Warning(_('Commission Account is not Found. Please go to Accounting-> Configuration and set the Sales commission account.'))
        else:
            account_id = self.env['account.account'].search([('id', '=', commission_account_id)])
            if not account_id:
                raise Warning(_('Commission Account is not Found. Please go to Accounting-> Configuration and set the Sales commission account.'))
        user_dict = {}
        target_line_obj = self.env['sales.target.line']
        self.env['sales.target'].search([('state', '=', 'confirmed')])._check_target_status()
        for commline in commission_ids:
            if not user_dict.get(commline.user_id.id):
                user_dict.update({commline.user_id.id: {'target': {}, 'without_target': []}})
            target_line_id = target_line_obj.search([('target_id.state', 'in', ['confirmed', 'closed']),
                                                   ('target_id.user_id', '=', commline.user_id.id),
                                                   ('start_date', '<=', commline.order_date),
                                                   ('end_date', '>=', commline.order_date)], order="id desc", limit=1)
            if target_line_id:
                if (target_line_id.target_state == 'open') or (target_line_id.start_date <= fields.Date.today() <= target_line_id.end_date):
                    continue
                if target_line_id.target_state == 'cancel':
                    user_dict[commline.user_id.id]['without_target'].append(commline)
                else:
                    if not user_dict[commline.user_id.id]['target'].get(target_line_id):
                        user_dict[commline.user_id.id]['target'].update({target_line_id: []})
                    user_dict[commline.user_id.id]['target'][target_line_id].append(commline)
            else:
                user_dict[commline.user_id.id]['without_target'].append(commline)
        lst_invoice_open = []
        for user, vals in user_dict.items():
            commission_lines = []
            userid = user_obj.browse(user)
            inv_line_data = []
            for commid in vals.get('without_target'):
                inv_line_data.append((0, 0, {'account_id': account_id.id,
                                             'name': commid.name + " Commission",
                                             'quantity': 1,
                                             'price_unit': commid.amount,
                                             'sale_commission_id': commid.id}))
                commission_lines.append(commid)
            for t_lineid, comm_ids in vals.get('target').items():
                if self.start_date and self.end_date:
                    cur_target_other_comm_ids = scobj.search([('state', '=', 'draft'), ('pay_by', '=', 'invoice'),
                                                              '|', ('invoice_id', '=', False), ('invoice_id.state', '=', 'cancel'),
                                                              ('user_id', '=', user),
                                                              ('order_date', '>=', t_lineid.start_date),
                                                              ('order_date', '<=', t_lineid.end_date)])
                    if len(cur_target_other_comm_ids) != len(comm_ids):
                        continue
                if (t_lineid.sales_amount >= t_lineid.target_amount) or self.override_target:
                    for commid in comm_ids:
                        inv_line_data.append((0, 0, {'account_id': account_id.id,
                                                     'name': commid.name + " Commission",
                                                     'quantity': 1,
                                                     'price_unit': commid.amount,
                                                     'sale_commission_id': commid.id}))
                        commission_lines.append(commid)
            if inv_line_data:
                on_change_vals = invoice_obj.onchange_partner_id('in_invoice', userid.partner_id.id, date_invoice=False,
                                                           payment_term=False, partner_bank_id=False, company_id=self.env.user.company_id.id)
                invoice_vals = {}
                if on_change_vals and on_change_vals.get('value'):
                    invoice_vals = on_change_vals['value']
                invoice_vals.update({'partner_id': userid.partner_id.id,
                                     'company_id': self.env.user.company_id.id,
                                     'commission_invoice': True,
                                     'type': 'in_invoice',
                                     'journal_id': journal_id.id,
                                     'invoice_line': inv_line_data,
                                     'origin': 'POS Commission Invoice',
                                     'date_due': datetime.today().date()})
                invoice_id = invoice_obj.search([('partner_id', '=', userid.partner_id.id),
                                                 ('state', '=', 'draft'), ('type', '=', 'in_invoice'),
                                                 ('commission_invoice', '=', True)], limit=1)
                if invoice_id:
                    invoice_id.write({'invoice_line': inv_line_data, 'commission_invoice': True})
                else:
                    invoice_id = invoice_obj.create(invoice_vals)
                lst_invoice_open.append(invoice_id.id)
                for commid in commission_lines:
                    commid.write({'invoice_id': invoice_id.id, 'state': 'invoiced'})
        if lst_invoice_open:
            action = self.env.ref('account.action_invoice_tree2').read()[0]
            action['display_name'] = _('Commission Invoice')
            action['domain'] = [('id', 'in', lst_invoice_open)]
            return action

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    user_ids = fields.Many2many('res.users', 'commission_payment_res_users_rel', string="User(s)")
    all_user = fields.Boolean(string="All Users")
    override_target = fields.Boolean(string='Override Target', help="If checked, then it will override user's Commission Target.")


class wizard_commission_summary(models.TransientModel):
    _name = 'wizard.commission.summary'

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    job_ids = fields.Many2many('hr.job', string="Job")
    user_ids = fields.Many2many('res.users', string="User(s)")
    state = fields.Selection([('draft', 'Draft'), ('invoiced', 'Invoiced'), ('paid', 'Paid'),
                              ('cancel', 'Cancel'), ('all', 'All')], string="Status", default='paid')

    @api.onchange('job_ids')
    def onchange_job(self):
        res = {'value': {'user_ids': False}}
        if self.job_ids:
            job_lst = [job.id for job in self.job_ids]
            emp_ids = self.env['hr.employee'].search([('user_id', '!=', False), ('job_id', 'in', job_lst)])
            user_lst = list(set([emp.user_id.id for emp in emp_ids]))
            res.update({'domain': {'user_ids': [('id', 'in', user_lst)]}})
            if self.env.context.get('ctx_job_user_report_print'):
                return user_lst
        return res

    @api.multi
    def get_users_commission(self):
        result = {}
        user_ids = [user.id for user in self.user_ids or self.env['res.users'].search([])]
        if not self.user_ids and self.job_ids:
            user_ids = self.with_context({'ctx_job_user_report_print': True}).onchange_job()
        domain = [('user_id', 'in', user_ids)]
        if self.start_date and self.end_date:
            domain.append(('order_date', '>=', str(self.start_date)))
            domain.append(('order_date', '<=', str(self.end_date)))
        if not self.state or self.state == 'all':
            domain += []
        else:
            domain += [('state', '=', self.state)]
        for commid in self.env['sales.commission'].search(domain, order="order_date"):
            vals = {'name': commid.name,
                    'date': commid.order_date,
                    'user_name': commid.user_id.name,
                    'amount': commid.amount,
                    'state': commid.state.title(),
                    'pay_by': 'Invoice' if commid.pay_by == 'invoice' else 'Salary'}
            if result.has_key(commid.user_id.id):
                result[commid.user_id.id].append(vals)
            else:
                result.update({commid.user_id.id: [vals]})
        if not result:
            raise Warning(_('Sales Commission Details not found.'))
        return result

    @api.multi
    def print_commission_report(self):
        if self.start_date > self.end_date:
            raise Warning(_('End Date should be greater than Start Date.'))
        datas = {
            'ids': self._ids,
            'model': 'wizard.commission.summary',
            'form': self.read()[0],
            'commission_details': self.get_users_commission()
        }
        return self.env['report'].get_action(self, 'aspl_pos_sales_commission.print_commission_summary_template', data=datas)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: