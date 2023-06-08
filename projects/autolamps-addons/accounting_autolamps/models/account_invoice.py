from openerp import api, fields, models
import requests


class account_invoice(models.Model):
	_inherit = 'account.invoice'

	esd_serial = fields.Char()
	sale_order_ids = fields.Many2many(
		'sale.order', 'sale_order_invoice_rel',
		'invoice_id', 'order_id', 'Sale Orders')

	@api.multi
	def invoice_validate(self):
		esd = self.env['ir.values'].sudo().get_default('account.config.settings', 'esd_server_address')
		if esd:
			try:
				timeout = self.env['ir.values'].sudo().get_default('account.config.settings', 'esd_timeout')
				timeout = timeout if timeout else 3
				r = requests.get(esd, timeout = timeout)
				self.esd_serial = r.text
			except:
				self.esd_serial = "###"
			res = super(account_invoice,self).invoice_validate()
			return res 

	@api.one
	def set_esd(self):
		esd = self.env['ir.values'].sudo().get_default('account.config.settings', 'esd_server_address')
		if esd:
			try:
				timeout = self.env['ir.values'].sudo().get_default('account.config.settings', 'esd_timeout')
				timeout = timeout if timeout else 3
				r = requests.get(esd, timeout=timeout)
				self.esd_serial = r.text
			except:
				self.esd_serial = "###"
