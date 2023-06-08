# -*- coding: utf-8 -*-
from openerp import http

# class SaccoLoanApprovals(http.Controller):
#     @http.route('/sacco_loan_approvals/sacco_loan_approvals/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sacco_loan_approvals/sacco_loan_approvals/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sacco_loan_approvals.listing', {
#             'root': '/sacco_loan_approvals/sacco_loan_approvals',
#             'objects': http.request.env['sacco_loan_approvals.sacco_loan_approvals'].search([]),
#         })

#     @http.route('/sacco_loan_approvals/sacco_loan_approvals/objects/<model("sacco_loan_approvals.sacco_loan_approvals"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sacco_loan_approvals.object', {
#             'object': obj
#         })