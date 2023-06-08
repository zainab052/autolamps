# -*- coding: utf-8 -*-
from openerp import http

# class ApprovalsCashManagement(http.Controller):
#     @http.route('/approvals_cash_management/approvals_cash_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/approvals_cash_management/approvals_cash_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('approvals_cash_management.listing', {
#             'root': '/approvals_cash_management/approvals_cash_management',
#             'objects': http.request.env['approvals_cash_management.approvals_cash_management'].search([]),
#         })

#     @http.route('/approvals_cash_management/approvals_cash_management/objects/<model("approvals_cash_management.approvals_cash_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('approvals_cash_management.object', {
#             'object': obj
#         })