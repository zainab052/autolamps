# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2008-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: Nilmar Shereef(<http://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import fields, models, api


class PlannedWork (models.Model):
    _name = 'planned.work'

    planned_work = fields.Many2one('product.template', string='Planned work', domain=[('type', '=', 'service')])
    time_spent = fields.Float(string='Estimated Time')
    work_date = fields.Datetime(string='Date')
    responsible = fields.Many2one('res.users', string='Responsible')
    work_id = fields.Many2one('car.workshop', string="Work id")
    work_cost = fields.Float(string="Service Cost")
    completed = fields.Boolean(string="Completed")
    duration = fields.Float(string='Duration')
    work_date2 = fields.Datetime(string='Date')

    @api.onchange('planned_work')
    def get_price(self):
        self.work_cost = self.planned_work.lst_price


class MaterialUsed (models.Model):
    _name = 'material.used'

    material = fields.Many2one('product.template', string='Products')
    amount = fields.Integer(string='Quantity')
    price = fields.Float(string='Unit Price')
    material_id = fields.Many2one(string='car.workshop')

    @api.onchange('material')
    def get_price(self):
        self.price = self.material.lst_price
