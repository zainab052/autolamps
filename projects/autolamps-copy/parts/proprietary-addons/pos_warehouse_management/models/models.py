# -*- coding: utf-8 -*-
#################################################################################
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#################################################################################
from openerp import api, fields, models, tools, _
from openerp.exceptions import ValidationError, Warning, RedirectWarning


class PosConfig(models.Model):
    _inherit = 'pos.config'
    related_stock_location_ids = fields.Many2many('stock.location', 'pos_config_stock_location_rel', 'pos_config_id',
                                                  'stock_location_id', string='Other Related Stock Locations', )
    create_related_picking_in_open_state = fields.Boolean(string="Create Related Picking in Open State", default=True,
                                                          help="Check this field to create related pickings in open state otherwise all related pickings are automatically validated and in done state.")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def get_product_stock_info(self, stock_info):
        result = {}
        stock_status = False
        for location_id in stock_info['location_ids']:
            product_obj = self.with_context(
                {'pricelist': stock_info['pricelist_id'], 'display_default_code': False, 'location': location_id})
            if (stock_info['stock_type'] == 'available_qty'):
                product_qty = product_obj.browse(stock_info['product_id']).qty_available
            elif (stock_info['stock_type'] == 'forecasted_qty'):
                product_qty = product_obj.browse(stock_info['product_id']).virtual_available
            else:
                product_qty = product_obj.browse(stock_info['product_id']).qty_available - product_obj.browse(
                    stock_info['product_id']).outgoing_qty
            if (product_qty > 0):
                stock_status = True
            stock_name = self.env['stock.location'].browse(location_id).display_name
            result[location_id] = [product_qty, location_id, stock_name]
        if stock_status:
            return result
        else:
            return False


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    stock_location_id = fields.Many2one('stock.location', string="Stock Location")


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    pos_order_id = fields.Many2one('pos.order', string="POS Order")


class PosOrder(models.Model):
    _inherit = 'pos.order'

    related_picking_id = fields.One2many('stock.picking', 'pos_order_id', readonly=True, string="Related Pickings")
    original_order_id = fields.Many2one('pos.order', string="Related Order")

    @api.multi
    def copy(self, default=None):
        res = super(PosOrder, self).copy(default)
        res.original_order_id = self.id
        return res

    @api.one
    def create_picking(self):
        """Create a picking for each order and validate it."""
        picking_obj = self.env['stock.picking']
        picking_type_obj = self.env['stock.picking.type']
        partner_obj = self.env['res.partner']
        move_obj = self.env['stock.move']
        StockWarehouse = self.env['stock.warehouse']
        picking_types = {}
        for p in self.env['stock.picking.type'].search([]):
            picking_types[p.default_location_dest_id.display_name + '_' + p.code] = p.id

        for order in self:
            if all(t == 'service' for t in order.lines.mapped('product_id.type')):
                continue
            addr = order.partner_id.address_get(['delivery']) or {}
            picking_type = order.picking_type_id
            picking_id = False
            location_id = order.location_id.id
            if order.amount_total < 0:
                location_id = order.original_order_id.location_id.id
            if order.partner_id:
                destination_id = order.partner_id.property_stock_customer.id
            else:
                if (not picking_type) or (not picking_type.default_location_dest_id):
                    customerloc, supplierloc = StockWarehouse._get_partner_locations()
                    destination_id = customerloc.id
                else:
                    destination_id = picking_type.default_location_dest_id.id
            stock_location_ids = []
            # All qties negative => Create negative
            for line in order.lines.filtered(lambda l: l.stock_location_id):
                stock_location_ids.append(line.stock_location_id.id)
            if picking_type and len(stock_location_ids) != len(order.lines.ids):
                pos_qty = all([x.qty >= 0 for x in order.lines])
                # Check negative quantities
                if order.amount_total >= 0:
                    picking_type = picking_type_obj.search([
                        ('code', '=', 'outgoing'),
                        ('default_location_src_id', '=', location_id)
                    ], limit=1)
                else:
                    picking_type = picking_type_obj.search([
                        ('code', '=', 'incoming'),
                        ('default_location_dest_id', '=', location_id)
                    ], limit = 1)
                picking_id = picking_obj.create({
                    'origin': order.name,
                    'partner_id': addr.get('delivery', False),
                    'date_done': order.date_order,
                    'picking_type_id': picking_type.id,
                    'company_id': order.company_id.id,
                    'move_type': 'direct',
                    'note': order.note or "",
                    'invoice_state': 'none',
                })
                order.write({'picking_id': picking_id.id})

            move_list = []

            for line in order.lines.filtered(
                    lambda l: l.product_id.type in ['product', 'consu'] and not l.stock_location_id):
                move_list.append(move_obj.create({
                    'name': line.name,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uos': line.product_id.uom_id.id,
                    'picking_id': picking_id and picking_id.id or False,
                    'picking_type_id': picking_type.id,
                    'product_id': line.product_id.id,
                    'product_uos_qty': abs(line.qty),
                    'product_uom_qty': abs(line.qty),
                    'state': 'draft',
                    'location_id': location_id if line.qty >= 0 else destination_id,
                    'location_dest_id': destination_id if line.qty >= 0 else location_id,
                }))
            stock_location_ids = list(set(stock_location_ids))

            for stock_location_id in stock_location_ids:
                loc_picking_id = False
                if order.amount_total >= 0:
                    picking_type = picking_type_obj.search([
                        ('code', '=', 'outgoing'),
                        ('default_location_src_id', '=', stock_location_id)
                    ], limit = 1)
                else:
                    picking_type = picking_type_obj.search([
                        ('code', '=', 'incoming'),
                        ('default_location_dest_id', '=', stock_location_id)
                    ], limit = 1)

                loc_picking_id = picking_obj.create({
                    'pos_order_id': order.id,
                    'origin': order.name,
                    'partner_id': addr.get('delivery', False),
                    'date_done': order.date_order,
                    'picking_type_id': picking_type.id,
                    'company_id': order.company_id.id,
                    'move_type': 'direct',
                    'note': order.note or "",
                    'invoice_state': 'none',
                })
                for line in order.lines.filtered(lambda l: l.stock_location_id.id == stock_location_id):
                    move_obj += move_obj.create({
                        'name': line.name,
                        'product_uom': line.product_id.uom_id.id,
                        'product_uos': line.product_id.uom_id.id,
                        'picking_id': loc_picking_id and loc_picking_id.id or False,
                        'picking_type_id': picking_type.id,
                        'product_id': line.product_id.id,
                        'product_uos_qty': abs(line.qty),
                        'product_uom_qty': abs(line.qty),
                        'state': 'draft',
                        'location_id': stock_location_id if line.qty >= 0 else destination_id,
                        'location_dest_id': destination_id if line.qty >= 0 else stock_location_id,
                    })
                if loc_picking_id:
                    loc_picking_id.action_confirm()
                    loc_picking_id.force_assign()
                    if order.session_id.config_id and not order.session_id.config_id.create_related_picking_in_open_state:
                        for pack in loc_picking_id.pack_operation_ids:
                            pack.write({'qty_done': pack.product_qty})
                        loc_picking_id.action_done()

                elif move_obj:
                    move_obj.action_confirm()
                    move_obj.force_assign()
                    move_obj.action_done()

            if picking_id:
                picking_id.action_confirm()
                picking_id.force_assign()
                for pack in picking_id.pack_operation_ids:
                    pack.write({'qty_done': pack.product_qty})
                picking_id.action_done()
            elif move_list:
                move_list.action_confirm()
                move_list.force_assign()
                move_list.action_done()
        return True
