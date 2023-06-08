# -*- coding: utf-8 -*-

from openerp import api, fields, models, exceptions


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    landed_cost_factor = fields.Float()
    base_pricing_factor = fields.Float()
    pricing_preference = fields.Selection([
        ('strict',"Strict"),
        ('high',"Prefer higher Price"),
        ('low',"Prefer Lower Price")
        ])
    costing_ids = fields.One2many('purchase.costing','order_id')

    @api.multi
    def print_xlsx_report(self):
        datas = {
            'ids': self.ids,
            'model': 'purchase.order',
            'form': self.read()[0]
        }

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'purchase.order.xlsx',
            'datas': datas,
            'name': 'Purchase Order'
        }

    @api.multi
    def compute_costing_lines(self):
        self.costing_ids.unlink()
        lines = []
        for record in self:
            for line in record.order_line:
                val = {}
                val['product_id'] = line.product_id
                val['old_cost'] = line.product_id.standard_price
                landed_cost = self.landed_cost_factor * line.price_unit if self.landed_cost_factor > 0 else line.product_id.standard_price
                val['new_cost'] = landed_cost
                val['old_price'] = line.product_id.lst_price
                price = self.base_pricing_factor * landed_cost if self.base_pricing_factor > 0 else line.product_id.lst_price
                
                if self.pricing_preference == "high":
                    val['new_price'] = round(price if price > line.product_id.lst_price else line.product_id.lst_price)
                elif self.pricing_preference == "low":
                    val['new_price'] = round(price if price < line.product_id.lst_price else line.product_id.lst_price)
                else:
                    val['new_price'] = round(price)

                val['new_price'] = round(float(val['new_price'])/10)*10 #round to nearest 10. Make sure price is a float for correct computation
                val['old_margin'] = line.product_id.lst_price - line.product_id.standard_price
                val['new_margin'] = val['new_price'] - val['new_cost']

                val['cost_difference'] = val['new_cost'] - val['old_cost']
                val['price_difference'] = val['new_price'] - val['old_price']

                lines.append((0, 0, val))

        self.costing_ids = lines

    @api.multi
    def adjust_costing(self):
        for record in self:
            for line in record.costing_ids:
                line.product_id.lst_price = line.new_price
                line.product_id.standard_price = line.new_cost

    @api.multi
    def revert_costing(self):
        for record in self:
            for line in record.costing_ids:
                line.product_id.lst_price = line.old_price
                line.product_id.standard_price = line.old_cost

    @api.one
    def update_supplier_pricelist(self):
        for product in self.order_line:
            supplier_pricelist = product.product_id.seller_ids.filtered(lambda x: x.name.id == self.partner_id.id)
            if len(supplier_pricelist)>0:
                for pricelist in supplier_pricelist:
                    pricelist.purchase_id = self.id
                    for line in pricelist.pricelist_ids:
                        line.price = product.price_unit

                

class PurchaseCosting(models.Model):
    _name = "purchase.costing"

    order_id = fields.Many2one('purchase.order')
    product_id = fields.Many2one('product.product', string="Product")
    old_cost = fields.Float(string="Old Cost")
    new_cost = fields.Float(string="New Cost")
    old_price =fields.Float(string="Old Price")
    new_price = fields.Float(string="New Price")
    old_margin = fields.Float(string="Old Margin")
    new_margin = fields.Float(string="New Margin")
    cost_difference = fields.Float(string="Cost Difference")
    price_difference = fields.Float(string="Price Difference")

class ProductSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    purchase_id = fields.Many2one('purchase.order', string="Last updated By PO", readonly=True)
