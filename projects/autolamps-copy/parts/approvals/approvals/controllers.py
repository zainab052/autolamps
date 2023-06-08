# -*- coding: utf-8 -*-
from openerp import http

# class Approvals(http.Controller):
#     @http.route('/approvals/approvals/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/approvals/approvals/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('approvals.listing', {
#             'root': '/approvals/approvals',
#             'objects': http.request.env['approvals.approvals'].search([]),
#         })

#     @http.route('/approvals/approvals/objects/<model("approvals.approvals"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('approvals.object', {
#             'object': obj
#         })