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


class commission_rule_group(models.Model):
    _name = 'commission.rule.group'

    name = fields.Char(string="Name", required=True)
    rule_ids = fields.One2many('commission.rule', 'rule_group_id', string="Rules")

    @api.constrains('rule_ids')
    def check_priority(self):
        if not self.rule_ids:
            raise Warning(_('Please define commission rules.'))
        if any(line.priority < 1 for line in self.rule_ids):
            raise Warning(_('Priority should not less than 1.'))
        if any(not line.beneficial_ids for line in self.rule_ids):
            raise Warning(_('Please define the Beneficial(s) into rules.'))
        for line in self.rule_ids:
            for benefid in line.beneficial_ids:
                if benefid.commission_price <= 0:
                    raise Warning(_('Into beneficial(s), Please enter the commission price/rate greater than 0.'))
                if benefid.compute_price_type == 'per' and benefid.commission_price >= 100:
                    raise Warning(_('Into beneficial(s), Commission rate for Percentage type must be between 0 to 100.'))
                if not benefid.job_id and not benefid.user_ids:
                    raise Warning(_('Into beneficial(s), set the Job position or User(s).'))
            if line.apply_on == '1':
                prod_ids = [x.product_id for x in line.product_line_ids]
                if len(prod_ids) == 0:
                    raise Warning(_('Please enter Products when you select Apply on \'Product Variant\'.'))
                if len(prod_ids) != len(set(prod_ids)):
                    raise Warning(_('You cannot set multiple times any product into single rule.'))
            if line.apply_on == '2':
                categ_ids = [x.category_id for x in line.category_line_ids]
                if len(categ_ids) == 0:
                    raise Warning(_('Please enter Product Category when you select Apply on \'Product Category\'.'))
                if len(categ_ids) != len(set(categ_ids)):
                    raise Warning(_('You cannot set multiple times any product category into single rule.'))

    def job_related_users(self, jobid):
        if jobid:
            empids = self.env['hr.employee'].search([('user_id', '!=', False), ('job_id', '=', jobid.id)])
            return [emp.user_id.id for emp in empids]
        return False

    def commission_amount(self, ruleid, jobid, userid, detail_data):
        for benef_id in ruleid.beneficial_ids:
            if benef_id.user_ids and userid.id in [user.id for user in benef_id.user_ids]:
                commission = detail_data['price_subtotal_incl'] * benef_id.commission_price / 100 if benef_id.compute_price_type == 'per' else benef_id.commission_price * detail_data['qty']
                return commission
            elif benef_id.job_id and not benef_id.user_ids:
                if userid.id in self.job_related_users(benef_id.job_id):
                    commission = detail_data['price_subtotal_incl'] * benef_id.commission_price / 100 if benef_id.compute_price_type == 'per' else benef_id.commission_price * detail_data['qty']
                    return commission
        return False

    @api.model
    def compute_commission_amount(self):
        pos_order_ids = self.env['pos.order'].search([('state', 'in', ['paid', 'done', 'invoiced']),
                                                      ('commission_calculated', '=', False)])
        date = fields.Date.today()
        emp_obj = self.env['hr.employee']
        rule_obj = self.env['commission.rule']
        result = []
        for order in pos_order_ids:
            if not order.lines.filtered(lambda l:l.qty > 0):
                continue  # skip the record if all qty <= 0
            employee_id = emp_obj.search([('user_id', '=', order.user_id.id), ('job_id', '!=', False)], limit=1)
            if order.session_id.config_id.comm_rule_group_id and employee_id:
                commission = 0.0
                flag = False
                dictcomm = {'order': order, 'commission': commission, 'user_sales_amount': 0.0,
                            'user_id': order.user_id.id, 'job_id': employee_id.job_id.id}
                orderlinevals = {'category': {}, 'product': {}}
                for poline in order.lines:
                    if not orderlinevals['product'].get(poline.product_id):
                        orderlinevals['product'].update({poline.product_id: {'price_subtotal_incl': 0,
                                                                             'qty': 0}})
                    if poline.product_id.pos_categ_id and not orderlinevals['category'].get(poline.product_id.pos_categ_id):
                        orderlinevals['category'].update({poline.product_id.pos_categ_id: {'price_subtotal_incl': 0,
                                                                             'qty': 0}})
                    orderlinevals['product'][poline.product_id]['price_subtotal_incl'] += poline.price_subtotal_incl
                    orderlinevals['product'][poline.product_id]['qty'] += poline.qty
                    if poline.product_id.pos_categ_id:
                        orderlinevals['category'][poline.product_id.pos_categ_id]['price_subtotal_incl'] += poline.price_subtotal_incl
                        orderlinevals['category'][poline.product_id.pos_categ_id]['qty'] += poline.qty
                self._cr.execute("""SELECT cr.id "ruleid", priority "prioriry", start_date, end_date
                                    FROM commission_rule cr
                                    WHERE (cr.start_date IS NULL OR cr.start_date <= '%s')
                                    AND (cr.end_date IS NULL OR cr.end_date >= '%s')
                                    AND apply_on IN ('1', '2')
                                    AND cr.rule_group_id = %s
                                    ORDER BY abs(start_date - '%s'), abs('%s' - end_date), priority, apply_on, cr.id
                                    """ % (date, date, order.session_id.config_id.comm_rule_group_id.id,
                                           date, date))
                match_rule_lst = self._cr.dictfetchall()
                for rule_id in match_rule_lst:
                    rid = self.env['commission.rule'].browse(rule_id['ruleid'])
                    if rid.apply_on == '1':
                        for prod, detail in orderlinevals['product'].items():
                            r_line = rid.product_line_ids.filtered(lambda l: l.product_id.id == prod.id)
                            if r_line and (r_line.min_criteria == 'min_amt' and r_line.min_value <= detail['price_subtotal_incl']) or \
                                          (r_line.min_criteria == 'min_qty' and r_line.min_value <= detail['qty']):
                                commissionvalue = self.commission_amount(rid, employee_id.job_id, order.user_id, detail)
                                if commissionvalue:
                                    commission += commissionvalue
                                    dictcomm['commission'] += commissionvalue
                                    dictcomm['user_sales_amount'] += detail['price_subtotal_incl']
                                    flag = True
                                    if prod.pos_categ_id and (prod.pos_categ_id in orderlinevals['category']):
                                        del orderlinevals['category'][prod.pos_categ_id]
                                    del orderlinevals['product'][prod]
                    elif rid.apply_on == '2':
                        for categ, detail in orderlinevals['category'].items():
                            r_line = rid.category_line_ids.filtered(lambda l: l.category_id.id == categ.id)
                            if r_line and (r_line.min_criteria == 'min_amt' and r_line.min_value <= detail['price_subtotal_incl']) or \
                                          (r_line.min_criteria == 'min_qty' and r_line.min_value <= detail['qty']):
                                commissionvalue = self.commission_amount(rid, employee_id.job_id, order.user_id, detail)
                                if commissionvalue:
                                    commission += commissionvalue
                                    dictcomm['commission'] += commissionvalue
                                    dictcomm['user_sales_amount'] += detail['price_subtotal_incl']
                                    flag = True
                                    del orderlinevals['category'][categ]
                                    remove_prod_lst = []
                                    for remove_prod in orderlinevals['product'].keys():
                                        if remove_prod.pos_categ_id.id == categ.id:
                                            remove_prod_lst.append(remove_prod)
                                    for each in remove_prod_lst:
                                        del orderlinevals['product'][each]
                if not flag:
                    commission = 0.0
                    dictcomm['commission'] = 0.0
                    dictcomm['user_sales_amount'] = 0.0
                    self._cr.execute("""SELECT cr.id "ruleid"
                            FROM commission_rule cr
                            WHERE (cr.start_date IS NULL OR cr.start_date <= '%s')
                            AND (cr.end_date IS NULL OR cr.end_date >= '%s')
                            AND apply_on IN ('3')
                            AND cr.rule_group_id = %s
                            AND min_amount <= '%s'
                            ORDER BY abs(start_date - '%s'), abs('%s' - end_date), priority, apply_on, cr.id
                        """ % (date, date, order.session_id.config_id.comm_rule_group_id.id,
                               order.amount_total, date, date))
                    match_rule_lst = self._cr.dictfetchall()
                    for ruleid in match_rule_lst:
                        rule_id = rule_obj.browse(ruleid['ruleid'])
                        # apply the commission
                        for benef_id in rule_id.beneficial_ids:
                            if benef_id.user_ids and order.user_id.id in [user.id for user in benef_id.user_ids]:
                                commission += order.amount_total * benef_id.commission_price / 100 if benef_id.compute_price_type == 'per' else benef_id.commission_price
                                flag = True
                                break
                            elif benef_id.job_id and not benef_id.user_ids:
                                if order.user_id.id in self.job_related_users(benef_id.job_id):
                                    commission += order.amount_total * benef_id.commission_price / 100 if benef_id.compute_price_type == 'per' else benef_id.commission_price
                                    flag = True
                                    break
                        if flag:
                            dictcomm['commission'] = commission
                            dictcomm['user_sales_amount'] = order.amount_total
                            break  # break this main loop, because when multiple rule is found at that time, only one rule is need to apply
                if flag:
                    result.append(dictcomm)
        commission_pay_by = self.env['ir.values'].sudo().get_default('account.config.settings', 'commission_pay_by')
        if commission_pay_by:
            comm_obj = self.env['sales.commission']
            for res in result:
                comm_obj.create({'name': res['order'].name,
                                 'pos_order_id': res['order'].id,
                                 'user_sales_amount': res['user_sales_amount'],
                                 'user_id': res['user_id'],
                                 'job_id': res['job_id'],
                                 'order_date': datetime.strptime(res['order'].date_order, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d'),
                                 'amount': res['commission'],
                                 'pay_by': commission_pay_by,
                                 'state': 'draft'})
        pos_order_ids.write({'commission_calculated': True})
        return True


class commission_rule(models.Model):
    _name = 'commission.rule'

    apply_on = fields.Selection([('1', 'Product Variant'),
                                 ('2', 'Product Category'),
                                 ('3', 'POS Order')], string="Apply on",
                                default="1", required=True)
    priority = fields.Integer(string="Priority", help="If rule priority is low, that rule consider first into\
                                                    commission calculation. 1 is lowest priority.", default=1)
    product_line_ids = fields.One2many('commission.rule.product', 'rule_id', string="Product(s)")
    category_line_ids = fields.One2many('commission.rule.category', 'rule_id', string="Category(s)")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    min_amount = fields.Float(string="Minimum Order Amount")
    beneficial_ids = fields.One2many('commission.beneficial', 'rule_ref_id', string='Beneficial(s)')
    rule_group_id = fields.Many2one('commission.rule.group', string="Commission Rule Group")

    @api.onchange('start_date', 'end_date')
    def onchange_start_end_date(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise Warning(_('Start Date should be less than End Date.'))


class commission_rule_product(models.Model):
    _name = 'commission.rule.product'

    rule_id = fields.Many2one('commission.rule', string="Rule")
    product_id = fields.Many2one('product.product', string="Product")
    min_criteria = fields.Selection([('min_amt', 'Min. Amount'), ('min_qty', 'Min. Qty')],
                                    default="min_amt", string="Criteria")
    min_value = fields.Float(string="Value")


class commission_rule_category(models.Model):
    _name = 'commission.rule.category'

    rule_id = fields.Many2one('commission.rule', string="Rule")
    category_id = fields.Many2one('pos.category', string="Category")
    min_criteria = fields.Selection([('min_amt', 'Min. Amount'), ('min_qty', 'Min. Qty')],
                                    default="min_amt", string="Criteria")
    min_value = fields.Float(string="Value")


class commission_beneficial(models.Model):
    _name = 'commission.beneficial'

    @api.onchange('job_id')
    def onchange_job_id(self):
        self.user_ids = False

    job_id = fields.Many2one('hr.job', string="Job Title")
    user_ids = fields.Many2many('res.users', string="User(s)")
    compute_price_type = fields.Selection([('fix_price', 'Fix Price'), ('per', 'Percentage')],
                                          string="Compute Price", default="per", required=True)
    commission_price = fields.Float(string="Commission Price/Rate")
    rule_ref_id = fields.Many2one('commission.rule', string='Rule Ref')

    @api.onchange('compute_price_type', 'commission_price')
    def onchange_compute_price_type(self):
        if self.compute_price_type == 'per' and self.commission_price > 100:
            raise Warning(_('Commission Rate must be less than 100%.'))


class res_users(models.Model):
    _inherit = 'res.users'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self.env.context.get('ctx_job_id'):
            emp_ids = self.env['hr.employee'].search([('user_id', '!=', False),
                                                      ('job_id', '=', self.env.context['ctx_job_id'])])
            args += [('id', 'in', [emp.user_id.id for emp in emp_ids])]
        return super(res_users, self).name_search(name=name, args=args, operator='ilike', limit=limit)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
