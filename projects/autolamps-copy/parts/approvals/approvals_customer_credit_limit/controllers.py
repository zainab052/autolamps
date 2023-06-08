# -*- coding: utf-8 -*-
from openerp import http

# class ApprovalsCustomerCreditLimit(http.Controller):
#     @http.route('/approvals_customer_credit_limit/approvals_customer_credit_limit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/approvals_customer_credit_limit/approvals_customer_credit_limit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('approvals_customer_credit_limit.listing', {
#             'root': '/approvals_customer_credit_limit/approvals_customer_credit_limit',
#             'objects': http.request.env['approvals_customer_credit_limit.approvals_customer_credit_limit'].search([]),
#         })

#     @http.route('/approvals_customer_credit_limit/approvals_customer_credit_limit/objects/<model("approvals_customer_credit_limit.approvals_customer_credit_limit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('approvals_customer_credit_limit.object', {
#             'object': obj
#         })