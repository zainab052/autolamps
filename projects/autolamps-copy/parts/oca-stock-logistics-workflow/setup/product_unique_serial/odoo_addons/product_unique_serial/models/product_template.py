# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2015 Vauxoo
#    Author: Moisés Lopez, Osval Reyes
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
##############################################################################
from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    lot_unique_ok = fields.Boolean('Unique lot',
                                   help='Forces set qty=1 '
                                        'to specify a Unique '
                                        'Serial Number for '
                                        'all moves')
