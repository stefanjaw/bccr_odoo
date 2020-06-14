# -*- coding: utf-8 -*-
# from odoo import http


# class Bccr(http.Controller):
#     @http.route('/bccr/bccr/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bccr/bccr/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bccr.listing', {
#             'root': '/bccr/bccr',
#             'objects': http.request.env['bccr.bccr'].search([]),
#         })

#     @http.route('/bccr/bccr/objects/<model("bccr.bccr"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bccr.object', {
#             'object': obj
#         })
