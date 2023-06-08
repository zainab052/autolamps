# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from openerp import http, SUPERUSER_ID
from openerp.http import request
import datetime
from openerp.addons.website_sale.controllers.main import website_sale


class odoo_website_sale(website_sale):

# When /shop/payment/validate done from backend create sales order, Validate, Create Invoice, Register Payment instead of Quotation...

    @http.route('/shop/payment/validate', type='http', auth="public", website=True)
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        cr, uid, context = request.cr, request.uid, request.context
        email_act = None
        sale_order_obj = request.registry['sale.order']
        
        website_order_obj = request.registry['website.config.settings']
        website_order_option = website_order_obj.browse(cr, uid,website_order_obj.search(cr, uid, [], limit=1, order="id desc")).website_order_configuration

        if transaction_id is None:
            tx = request.website.sale_get_transaction()
        else:
            tx = request.registry['payment.transaction'].browse(cr, uid, transaction_id, context=context)

        if sale_order_id is None:
            order = request.website.sale_get_order(context=context)
        else:
            order = request.registry['sale.order'].browse(cr, SUPERUSER_ID, sale_order_id, context=context)
            assert order.id == request.session.get('sale_last_order_id')

        if not order or (order.amount_total and not tx):
            return request.redirect('/shop')

        if (not order.amount_total and not tx) or tx.state in ['pending', 'done']:
            #if (not order.amount_total and not tx):
                # Orders are confirmed by payment transactions, but there is none for free orders,
                # (e.g. free events), so confirm immediately
            order.with_context(dict(context, send_email=True)).action_button_confirm()
            order.force_quotation_send() # Send Mail when order placed from webshop
            order.payment_acquirer_id.website_order_msg = 'confirm'

            # This code is for invoice_policy = order
            #item_count = 0
            #count = 0
            #for item in order.order_line:
                #item_count+=1
                #if item.product_id.invoice_policy == 'order':
                    #count+=1
                #print "iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii", item_count
                #if item_count != count:
                    #return request.redirect('/shop/confirmation')
            
            if website_order_option == 'invoice' or website_order_option == 'validate' or website_order_option == 'payment':
                advance_payment = request.registry['sale.advance.payment.inv']
                advance_create = advance_payment.create(cr, SUPERUSER_ID, {'advance_payment_method': 'all'}, context=context)
                advance_browse = advance_payment.browse(cr, SUPERUSER_ID, advance_create, context=context)
                advance_final = advance_browse.with_context(dict(context, active_ids= [order.id], open_invoices=False)).create_invoices()
                
                
                
                order.payment_acquirer_id.website_order_msg = 'invoice'

            if website_order_option == 'validate' or website_order_option == 'payment':                
                account_invoice = request.registry['account.invoice']
                account_search = account_invoice.search(cr, SUPERUSER_ID, [('origin', '=', order.name)], context=context)
                account_browse = account_invoice.browse(cr, SUPERUSER_ID, account_search, context=context)
                for a in account_browse:
                	a.action_date_assign()
                	a.action_move_create()
                	a.invoice_validate()
                order.payment_acquirer_id.website_order_msg = 'validate'
                	
            if website_order_option == 'payment':
			
                account_payment = request.registry['account.voucher']
                if order.payment_acquirer_id.journal_id:
                    journal = order.payment_acquirer_id.journal_id.id
                else:
                    return request.redirect('/shop/confirmation')
                vals = { 'journal_id': journal, 'state': 'draft', 'type': 'receipt', 'amount':account_browse.amount_total, 'currency_id': account_browse.currency_id.id, 'date': datetime.datetime.now().date(), 'partner_id': account_browse.partner_id.id, 'account_id':order.payment_acquirer_id.journal_id.default_debit_account_id.id}
                payment_create = account_payment.create(cr, SUPERUSER_ID, vals, context=context)
                
                
                
                payment_browse = account_payment.browse(cr, SUPERUSER_ID, payment_create, context=context)
                payment_browse.invoice_ids = [(4, account_browse.id)]
                
                
                validate = payment_browse.with_context(destination_account_id=account_browse.account_id.id).proforma_voucher()
                account_browse.state = 'paid'
                order.payment_acquirer_id.website_order_msg = 'payment'
                

        elif tx and tx.state == 'cancel':
            # cancel the quotation
            sale_order_obj.action_cancel(cr, SUPERUSER_ID, [order.id], context=request.context)

        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset(context=context)
        if tx and tx.state == 'draft':
            return request.redirect('/shop')

        return request.redirect('/shop/confirmation')
    	
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        
