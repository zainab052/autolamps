# -*- coding: utf-8 -*-
#
#    Jamotion GmbH, Your Odoo implementation partner
#    Copyright (C) 2013-2015 Jamotion GmbH.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Created by renzo.meister on 20.03.2016.
#
# imports of python lib
import logging

# imports of openerp
from openerp import models, fields, api, _

# imports from odoo modules

# global variable definitions
_logger = logging.getLogger(__name__)


class PaymentAcquirer(models.Model):
    # Private attributes
    _inherit = 'payment.acquirer'

    # Default methods

    # Fields declaration
    payment_method_id = fields.Many2one(
        comodel_name='payment.method',
        string='Payment Method',
        ondelete='restrict',
    )

    # compute and search fields, in the same order that fields declaration

    # Constraints and onchanges

    # CRUD methods

    # Action methods

    # Business methods


class PaymentTransaction(models.Model):
    # Private attributes
    _inherit = 'payment.transaction'

    # Default methods

    # Fields declaration

    # compute and search fields, in the same order that fields declaration

    # Constraints and onchanges

    # CRUD methods
    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        """
        If state is set to done, try for automatic payment
        :param vals:
        :return:
        """
        result = super(PaymentTransaction, self).create(vals)
        if 'state' in vals and vals['state'] == 'done':
            result._set_order_attributes_and_add_payment()
        return result

    @api.multi
    def write(self, vals):
        """
        If state is set to done, try for automatic payment
        :param vals:
        :return:
        """
        result = super(PaymentTransaction, self).write(vals)
        if 'state' in vals and vals['state'] == 'done':
            self._set_order_attributes_and_add_payment()
        return result

    # Action methods

    # Business methods
    @api.multi
    def _set_order_attributes_and_add_payment(self):
        """
        Check if a payment method is set on the payment acquirer. If it is set, update sale order settings and
        create the account move for the online payment based on payment method.
        """
        for record in self:
            if not record.sale_order_id or not record.acquirer_id or not record.acquirer_id.payment_method_id:
                continue
            _logger.info('Adding payment for sale order {0}'.format(record.sale_order_id.name))
            record.sale_order_id.payment_method_id = record.acquirer_id.payment_method_id
            record.sale_order_id.onchange_payment_method_set_workflow()
            record.sale_order_id.onchange_payment_method_id_set_payment_term()
            record.sale_order_id.onchange_workflow_process_id()
            record.sale_order_id.automatic_payment(record.amount)
