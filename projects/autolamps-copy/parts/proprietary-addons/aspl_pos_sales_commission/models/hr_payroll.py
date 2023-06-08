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


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    sale_commission_amount = fields.Float(string="Commission Amount", readonly=True, copy=False)
    override_target = fields.Boolean(string='Override Target', help="If checked, then it will override user's Commission Target.",
                                     states={'draft': [('readonly', False)]}, readonly=True, copy=False)
    commission_line_ids = fields.Many2many('sales.commission', 'table_pos_sales_commission_hr_payslip_relation',
                                           string="Commission Lines", readonly=True, copy=False)

    @api.multi
    def compute_sheet(self):
        scobj = self.env['sales.commission']
        target_line_obj = self.env['sales.target.line']
        self.env['sales.target'].search([('state', '=', 'confirmed')])._check_target_status()
        for payslip in self:
            commission_lines = scobj
            commission = 0.0
            payslip.commission_line_ids = False
            if payslip.employee_id.user_id:
                comm_ids = scobj.search([('user_id', '=', payslip.employee_id.user_id.id),
                                        ('order_date', '<=', payslip.date_from),
                                        ('pay_by', '=', 'salary'), ('state', '=', 'draft')])
                user_dict = {}
                for commline in comm_ids:
                    if not user_dict.get(commline.user_id.id):
                        user_dict.update({commline.user_id.id: {'target': {}, 'without_target': []}})
                    target_line_id = target_line_obj.search([('target_id.state', 'in', ['confirmed', 'closed']),
                                                            ('target_id.user_id', '=', commline.user_id.id),
                                                            ('start_date', '<=', commline.order_date),
                                                            ('end_date', '>=', commline.order_date)])
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
                for vals in user_dict.values():
                    for commid in vals.get('without_target'):
                        commission += commid.amount
                        commission_lines += commid
                    for t_lineid, comm_ids in vals.get('target').items():
                        if payslip.date_from and payslip.date_to:
                            cur_target_other_comm_ids = scobj.search([('user_id', '=', payslip.employee_id.user_id.id),
                                                    ('order_date', '>=', t_lineid.start_date),
                                                    ('order_date', '<=', t_lineid.end_date),
                                                    ('pay_by', '=', 'salary'), ('state', '=', 'draft')])
                            if len(cur_target_other_comm_ids) != len(comm_ids):
                                continue
                        if (t_lineid.sales_amount >= t_lineid.target_amount) or payslip.override_target:
                            for commid in comm_ids:
                                commission += commid.amount
                                commission_lines += commid
            payslip.sale_commission_amount = commission
            payslip.commission_line_ids = commission_lines
        return super(hr_payslip, self).compute_sheet()

    @api.multi
    def hr_verify_sheet(self):
        res = super(hr_payslip, self).hr_verify_sheet()
        comm_rule_id = self.env.ref('aspl_pos_sales_commission.hr_salary_rule_aspl_sales_commission')
        if comm_rule_id:
            for payslip in self:
                if payslip.employee_id.user_id and comm_rule_id.id in [line.salary_rule_id.id for line in payslip.line_ids]:
                    payslip.commission_line_ids.write({'state': 'paid', 'payslip_id': payslip.id})
        return res


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def commission_graph(self):
        if self.user_id:
            comm_ids = self.env['sales.commission'].search([('user_id', '=', self.user_id.id)])
            if comm_ids:
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Sales Commission Graph'),
                    'res_model': 'sales.commission',
                    'view_type': 'form',
                    'view_mode': 'graph',
                    'domain': [('id', 'in', [each.id for each in comm_ids])],
                }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: